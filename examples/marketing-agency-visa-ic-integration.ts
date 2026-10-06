/**
 * Accepting agent payments as a marketing agency — MERCHANT SIDE, with the agent side shown for context.
 *
 * SIMPLIFIED EXAMPLE. Not affiliated with or reviewed by Visa. Replace the adapters with your payment
 * processor's SDK and Visa's toolkit, and test in sandbox before going live.
 *
 * Roles in Visa Intelligent Commerce (VIC):
 *   - The AGENT PLATFORM enrolls the cardholder's card, records what the cardholder approved (a
 *     "purchase instruction"), and retrieves single-use credentials per checkout.
 *     -> setupAgentCredential() below wraps that; templates in visa-ic-skills/agent-payment-setup.ts.
 *   - The MERCHANT (this agency) verifies the agent, prices the order from its own catalog, charges the
 *     tokenized credentials through its normal acquirer or processor, and provisions the service.
 *     -> initiateAgentPayment() below.
 *   The merchant never creates the agent's token and never sees the cardholder's real card number.
 *
 * Docs:
 *   - VIC overview:          https://developer.visa.com/capabilities/visa-intelligent-commerce
 *   - VIC developer guide:   https://developer.visaacceptance.com/docs/vas/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce.html
 *   - Visa's toolkit:        https://github.com/visa/ai
 *   - Trusted Agent Protocol (agent verification): see Visa's developer docs; built on HTTP Message
 *     Signatures (RFC 9421).
 */

import {
  createAgentCredential,
  createPurchaseInstruction,
  type AgentCredential,
  type PurchaseInstruction,
  type PurchaseMandate,
  type TransactionCredentials,
  type VicClient,
  type VicPayloads,
} from "../visa-ic-skills/agent-payment-setup";

// =============================================================================================
// Merchant-side adapters you implement
// =============================================================================================

/** Your catalog: the same data behind the get_pricing WebMCP tool. Prices come from here, never from the agent. */
export interface Catalog {
  getOffer(packageId: string): Promise<Offer | null>;
}

export interface Offer {
  packageId: string;
  name: string;
  priceMinor: number;            // integer cents
  currency: string;              // "USD"
  purchasableByAgent: boolean;   // false for anything that needs a sales conversation
}

/** Verifies the agent's signed request (Trusted Agent Protocol). Implement per Visa's spec. */
export interface AgentVerifier {
  verify(request: { method: string; url: string; headers: Record<string, string> }): Promise<VerifiedAgent | null>;
}

export interface VerifiedAgent {
  agentId: string;
  agentName: string;
}

/**
 * Your acquirer or payment processor (for example Visa Acceptance / Cybersource). Agent payments arrive
 * as tokenized card credentials; charge them like any card-not-present tokenized payment.
 */
export interface PaymentProcessor {
  authorizeAndCapture(input: {
    amountMinor: number;
    currency: string;
    credentials: TransactionCredentials;
    orderId: string;
    idempotencyKey: string;
    agentId: string;             // keep for disputes and reporting
  }): Promise<{ status: "approved" | "declined"; processorReference: string; declineReason?: string }>;
}

/** Creates orders, records audit trails, and starts the service. */
export interface OrderStore {
  findByIdempotencyKey(key: string): Promise<Receipt | null>;
  create(order: { orderId: string; offer: Offer; agent: VerifiedAgent; buyerEmail: string; approvalRef: string }): Promise<void>;
  markPaid(orderId: string, processorReference: string): Promise<void>;
  markFailed(orderId: string, reason: string): Promise<void>;
}

export interface Provisioner {
  /** Starts the service immediately: create the workspace, send onboarding, schedule kickoff. */
  provision(orderId: string, offer: Offer, buyerEmail: string): Promise<{ onboardingUrl: string }>;
}

// =============================================================================================
// Errors: specific, readable codes the agent can act on
// =============================================================================================

export type AgentPaymentErrorCode =
  | "AGENT_NOT_VERIFIED"   // unsigned or unknown agent: refuse, don't guess
  | "APPROVAL_MISSING"     // the person hasn't approved this purchase
  | "OFFER_NOT_FOUND"
  | "OFFER_NOT_AGENT_PURCHASABLE" // route to submit_agency_inquiry instead
  | "PRICE_MISMATCH"       // the agent quoted a stale or wrong price
  | "PAYMENT_DECLINED"
  | "PROVISIONING_FAILED"; // payment succeeded but setup failed: escalate to a human

export class AgentPaymentError extends Error {
  constructor(readonly code: AgentPaymentErrorCode, message: string, readonly retryable = false) {
    super(message);
    this.name = "AgentPaymentError";
  }
}

// =============================================================================================
// Merchant side: accept an agent payment and provision the service
// =============================================================================================

export interface AgentPaymentRequest {
  packageId: string;               // from discover_seo_services / get_pricing
  quotedPriceMinor: number;        // the price the agent showed the person
  currency: string;
  buyerEmail: string;
  userApproval: {
    approved: true;                // the person explicitly approved this purchase
    approvalRef: string;           // reference to that approval (e.g. the VIC instruction id)
  };
  credentials: TransactionCredentials; // single-use, retrieved by the agent from VIC for this checkout
  idempotencyKey: string;          // the agent's transaction reference; the same key returns the same result
  http: { method: string; url: string; headers: Record<string, string> }; // for agent verification
}

export interface Receipt {
  orderId: string;
  status: "paid";
  amountMinor: number;
  currency: string;
  processorReference: string;
  onboardingUrl: string;
}

export interface MerchantDeps {
  catalog: Catalog;
  verifier: AgentVerifier;
  processor: PaymentProcessor;
  orders: OrderStore;
  provisioner: Provisioner;
  newOrderId: () => string;
}

/**
 * Accepts a payment from a verified agent for a fixed-price package and provisions it immediately.
 *
 * Order of checks matters: verify the agent and the approval BEFORE touching the card credentials, and
 * price from your own catalog, never from the request.
 */
export async function initiateAgentPayment(deps: MerchantDeps, req: AgentPaymentRequest): Promise<Receipt> {
  // 0. Idempotency: agents retry on timeouts. The same key must never charge twice.
  const existing = await deps.orders.findByIdempotencyKey(req.idempotencyKey);
  if (existing) return existing;

  // 1. Who is calling? Refuse unsigned or unknown agents.
  const agent = await deps.verifier.verify(req.http);
  if (!agent) {
    throw new AgentPaymentError("AGENT_NOT_VERIFIED", "Agent signature could not be verified.");
  }

  // 2. Did a person approve this purchase?
  if (req.userApproval?.approved !== true || !req.userApproval.approvalRef) {
    throw new AgentPaymentError("APPROVAL_MISSING", "This purchase needs the person's explicit approval.");
  }

  // 3. Is this offer for sale to agents, at this price?
  const offer = await deps.catalog.getOffer(req.packageId);
  if (!offer) throw new AgentPaymentError("OFFER_NOT_FOUND", `No package ${req.packageId}.`);
  if (!offer.purchasableByAgent) {
    throw new AgentPaymentError(
      "OFFER_NOT_AGENT_PURCHASABLE",
      "This package needs a conversation first. Use submit_agency_inquiry instead.",
    );
  }
  if (offer.priceMinor !== req.quotedPriceMinor || offer.currency !== req.currency) {
    throw new AgentPaymentError(
      "PRICE_MISMATCH",
      `Current price is ${offer.priceMinor} ${offer.currency} (minor units). Re-confirm with the person.`,
    );
  }

  // 4. Create the order, then charge the tokenized credentials through your processor.
  const orderId = deps.newOrderId();
  await deps.orders.create({ orderId, offer, agent, buyerEmail: req.buyerEmail, approvalRef: req.userApproval.approvalRef });

  const payment = await deps.processor.authorizeAndCapture({
    amountMinor: offer.priceMinor,
    currency: offer.currency,
    credentials: req.credentials,   // passed straight through; never logged or stored
    orderId,
    idempotencyKey: req.idempotencyKey,
    agentId: agent.agentId,
  });
  if (payment.status !== "approved") {
    await deps.orders.markFailed(orderId, payment.declineReason ?? "declined");
    throw new AgentPaymentError("PAYMENT_DECLINED", "The payment was declined. No charge was made.", true);
  }
  await deps.orders.markPaid(orderId, payment.processorReference);

  // 5. Provision immediately. If this fails, the person has paid: escalate, don't silently retry forever.
  try {
    const { onboardingUrl } = await deps.provisioner.provision(orderId, offer, req.buyerEmail);
    return {
      orderId,
      status: "paid",
      amountMinor: offer.priceMinor,
      currency: offer.currency,
      processorReference: payment.processorReference,
      onboardingUrl,
    };
  } catch {
    throw new AgentPaymentError(
      "PROVISIONING_FAILED",
      "Payment succeeded but setup failed. Our team has been notified and will contact you.",
    );
  }
}

// =============================================================================================
// Agent side (context): set up an agent credential linked to this merchant
// =============================================================================================

/**
 * Runs in the AGENT PLATFORM, not on the agency's site. Shown here so the full flow is visible.
 *
 * 1. Enrolls the cardholder's card for the agent (agent-specific token; requires the cardholder's
 *    passkey setup to have been completed first).
 * 2. Records a purchase instruction scoped to ONE merchant (this agency), a cap and an expiry: this is
 *    what "links" the credential to the merchant.
 *
 * Returns what the agent needs to pay later. The agent then retrieves single-use credentials with
 * initiatePayment() from visa-ic-skills/agent-payment-setup.ts and calls initiateAgentPayment() above.
 */
export async function setupAgentCredential(
  vic: VicClient,
  payloads: VicPayloads,
  input: {
    consumerId: string;
    enrollmentReferenceId: string;
    merchant: { name: string; url: string };
    description: string;
    maxAmountMinor: number;
    currency: string;
    validForDays: number;
  },
): Promise<{ credential: AgentCredential; instruction: PurchaseInstruction }> {
  const credential = await createAgentCredential(vic, payloads, {
    consumerId: input.consumerId,
    enrollmentReferenceId: input.enrollmentReferenceId,
  });

  const mandate: PurchaseMandate = {
    merchantName: input.merchant.name,
    merchantUrl: input.merchant.url,
    description: input.description,
    maxAmountMinor: input.maxAmountMinor,
    currency: input.currency,
    expiresAt: new Date(Date.now() + input.validForDays * 86_400_000).toISOString(),
  };
  const instruction = await createPurchaseInstruction(vic, payloads, {
    consumerId: input.consumerId,
    tokenId: credential.tokenId,
    mandate,
  });
  return { credential, instruction };
}

// =============================================================================================
// Example: mapping errors to agent-readable responses (e.g. in your WebMCP tool's execute())
// =============================================================================================

export function toToolResult(err: unknown): { content: Array<{ type: "text"; text: string }> } {
  if (err instanceof AgentPaymentError) {
    return {
      content: [{
        type: "text",
        text: JSON.stringify({ error: err.code, message: err.message, retryable: err.retryable }),
      }],
    };
  }
  // Unknown errors: don't leak internals to the agent.
  return { content: [{ type: "text", text: JSON.stringify({ error: "INTERNAL", message: "Something went wrong. Retrying with the same idempotencyKey is safe and will not charge twice." }) }] };
}
