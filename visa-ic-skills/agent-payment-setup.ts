/**
 * Visa Intelligent Commerce (VIC) function templates — AGENT SIDE.
 *
 * SIMPLIFIED EXAMPLE. Not affiliated with or reviewed by Visa. Adapt, review and test in Visa's
 * sandbox before any production use.
 *
 * Who runs this code: the AGENT PLATFORM (the AI assistant acting for a cardholder), not the merchant.
 * A marketing agency selling services is the merchant; its side is in
 * examples/marketing-agency-visa-ic-integration.ts.
 *
 * The VIC flow these templates follow (matches the public examples in https://github.com/visa/ai):
 *   1. enrollCard                  POST /vacp/v1/cards                         (once per card + agent)
 *   2. initiatePurchaseInstruction POST /vacp/v1/instructions                  (what the cardholder approved)
 *   3. getTransactionCredentials   POST /vacp/v1/instructions/{id}/credentials (per checkout)
 *   4. sendConfirmations           POST /vacp/v1/instructions/{id}/confirmations (after checkout)
 *   plus updatePurchaseInstruction / cancelPurchaseInstruction.
 *
 * Official docs:
 *   - https://developer.visa.com/capabilities/visa-intelligent-commerce
 *   - https://developer.visaacceptance.com/docs/vas/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce.html
 *   - https://github.com/visa/ai  (VicApiClient in packages/api-client; payload builders in apps/shared-utils)
 *
 * Design choices:
 *   - No dependency on an npm package: Visa's @visa/api-client is built from source in github.com/visa/ai.
 *     These templates depend on two small interfaces you implement with it (VicClient, VicPayloads).
 *   - Real card numbers never appear here. Credentials are retrieved per transaction and passed straight
 *     to checkout; never log or store them.
 *   - Every purchase is checked against what the cardholder approved before credentials are requested.
 */

// ---------------------------------------------------------------------------------------------
// Adapters you implement
// ---------------------------------------------------------------------------------------------

/** Mirrors the method names of VicApiClient in github.com/visa/ai (packages/api-client). */
export interface VicClient {
  enrollCard<T>(request: Record<string, unknown>): Promise<T>;
  initiatePurchaseInstruction<T>(request: Record<string, unknown>): Promise<T>;
  updatePurchaseInstruction<T>(instructionId: string, request: Record<string, unknown>): Promise<T>;
  cancelPurchaseInstruction<T>(instructionId: string, request: Record<string, unknown>): Promise<T>;
  getTransactionCredentials<T>(instructionId: string, request: Record<string, unknown>): Promise<T>;
  sendConfirmations<T>(instructionId: string, request: Record<string, unknown>): Promise<T>;
}

/**
 * Builds the real VIC request bodies. Implement with Visa's payload builders
 * (apps/shared-utils/payload-builders in github.com/visa/ai) so field names match the API exactly.
 */
export interface VicPayloads {
  enrollCard(input: { consumerId: string; enrollmentReferenceId: string }): Record<string, unknown>;
  purchaseInstruction(input: { consumerId: string; tokenId: string; mandate: PurchaseMandate }): Record<string, unknown>;
  credentials(input: { tokenId: string; transactionReferenceId: string }): Record<string, unknown>;
  confirmation(input: { transactionReferenceId: string; outcome: CheckoutOutcome }): Record<string, unknown>;
  cancel(input: { reason: string }): Record<string, unknown>;
}

// ---------------------------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------------------------

/** What the cardholder approved. Keep it narrow: one merchant, a cap, an expiry. */
export interface PurchaseMandate {
  merchantName: string;
  merchantUrl: string;
  description: string;          // e.g. "SEO Growth package, first month"
  maxAmountMinor: number;       // integer minor units (cents) to avoid float rounding
  currency: string;             // ISO 4217, e.g. "USD"
  expiresAt: string;            // ISO 8601
  recurring?: { interval: "month"; maxCycles: number };
}

export interface VicResponse<D> {
  data: D;
  correlationId?: string;
}

export interface AgentCredential {
  clientReferenceId: string;
  tokenId: string;              // the agent-specific token reference (never a card number)
  status: string;
}

export interface PurchaseInstruction {
  instructionId: string;
  mandate: PurchaseMandate;
  status?: string;
}

/** Single-use credentials for one checkout. Treat as secret: never log, persist or send to a model. */
export interface TransactionCredentials {
  cardNumber?: string;          // network token, not the cardholder's real card number
  expirationDate?: string;
  securityCode?: string;        // dynamic, single-use
}

export type CheckoutOutcome = "approved" | "declined" | "cancelled";

export class VicError extends Error {
  constructor(
    message: string,
    readonly code:
      | "ENROLLMENT_FAILED"
      | "MANDATE_EXCEEDED"
      | "MANDATE_EXPIRED"
      | "INSTRUCTION_FAILED"
      | "CREDENTIALS_FAILED"
      | "CONFIRMATION_FAILED"
      | "WEBHOOK_REJECTED",
    readonly cause?: unknown,
  ) {
    super(message);
    this.name = "VicError";
  }
}

// ---------------------------------------------------------------------------------------------
// 1. Create an agent credential (enroll a card for this agent)
// ---------------------------------------------------------------------------------------------

/**
 * Enrolls the cardholder's card for this agent. Before calling, the cardholder must already have
 * completed card tokenization and Visa Payment Passkey setup in your app (see vic-agent/ in
 * github.com/visa/ai for that flow); `enrollmentReferenceId` comes from that step.
 *
 * @example
 *   const cred = await createAgentCredential(vic, payloads, { consumerId: "user-123", enrollmentReferenceId });
 */
export async function createAgentCredential(
  vic: VicClient,
  payloads: VicPayloads,
  input: { consumerId: string; enrollmentReferenceId: string },
): Promise<AgentCredential> {
  try {
    const res = await vic.enrollCard<VicResponse<{ clientReferenceId: string; status: string }>>(
      payloads.enrollCard(input),
    );
    return {
      clientReferenceId: res.data.clientReferenceId,
      tokenId: input.enrollmentReferenceId,
      status: res.data.status,
    };
  } catch (err) {
    throw new VicError("Card enrollment failed. Ask the cardholder to retry setup.", "ENROLLMENT_FAILED", err);
  }
}

// ---------------------------------------------------------------------------------------------
// 2. Initiate a payment (purchase instruction -> credentials -> checkout -> confirmation)
// ---------------------------------------------------------------------------------------------

/** Rejects a purchase that falls outside what the cardholder approved. Pure function: unit-test it. */
export function assertWithinMandate(
  mandate: PurchaseMandate,
  purchase: { merchantUrl: string; amountMinor: number; currency: string },
  now: Date = new Date(),
): void {
  if (new Date(mandate.expiresAt).getTime() <= now.getTime()) {
    throw new VicError("The cardholder's approval has expired. Ask them to approve again.", "MANDATE_EXPIRED");
  }
  if (new URL(purchase.merchantUrl).origin !== new URL(mandate.merchantUrl).origin) {
    throw new VicError("This merchant is not the one the cardholder approved.", "MANDATE_EXCEEDED");
  }
  if (purchase.currency !== mandate.currency || purchase.amountMinor > mandate.maxAmountMinor) {
    throw new VicError("The amount exceeds what the cardholder approved.", "MANDATE_EXCEEDED");
  }
}

/** Records the cardholder's approval with VIC. Call once per approval, not once per checkout. */
export async function createPurchaseInstruction(
  vic: VicClient,
  payloads: VicPayloads,
  input: { consumerId: string; tokenId: string; mandate: PurchaseMandate },
): Promise<PurchaseInstruction> {
  try {
    const res = await vic.initiatePurchaseInstruction<VicResponse<{ instructionId: string; status?: string }>>(
      payloads.purchaseInstruction(input),
    );
    return { instructionId: res.data.instructionId, mandate: input.mandate, status: res.data.status };
  } catch (err) {
    throw new VicError("Could not record the purchase approval with Visa.", "INSTRUCTION_FAILED", err);
  }
}

/**
 * Pays one merchant within an existing instruction.
 *
 * `checkout` is your code that submits the single-use credentials to the merchant (for example via
 * the merchant's agent checkout endpoint). It must not log the credentials.
 */
export async function initiatePayment(
  vic: VicClient,
  payloads: VicPayloads,
  input: {
    tokenId: string;
    instruction: PurchaseInstruction;
    purchase: { merchantUrl: string; amountMinor: number; currency: string };
    transactionReferenceId: string;   // your unique id for this checkout; reuse it on retries
    checkout: (credentials: TransactionCredentials) => Promise<CheckoutOutcome>;
  },
): Promise<CheckoutOutcome> {
  assertWithinMandate(input.instruction.mandate, input.purchase);

  let credentials: TransactionCredentials | undefined;
  try {
    const res = await vic.getTransactionCredentials<
      VicResponse<{ instructionId: string; transactionCredentials?: TransactionCredentials }>
    >(input.instruction.instructionId, payloads.credentials({
      tokenId: input.tokenId,
      transactionReferenceId: input.transactionReferenceId,
    }));
    credentials = res.data.transactionCredentials;
  } catch (err) {
    throw new VicError("Could not retrieve payment credentials.", "CREDENTIALS_FAILED", err);
  }
  if (!credentials) {
    throw new VicError("Visa returned no credentials for this instruction.", "CREDENTIALS_FAILED");
  }

  const outcome = await input.checkout(credentials);
  credentials = undefined; // drop the reference as soon as checkout is done

  try {
    await vic.sendConfirmations(input.instruction.instructionId, payloads.confirmation({
      transactionReferenceId: input.transactionReferenceId,
      outcome,
    }));
  } catch (err) {
    // The payment already happened; surface the failure so it can be retried, don't hide it.
    throw new VicError("Payment completed but confirmation to Visa failed. Retry confirmation.", "CONFIRMATION_FAILED", err);
  }
  return outcome;
}

// ---------------------------------------------------------------------------------------------
// 3. Manage the wallet (the agent's approved instructions)
// ---------------------------------------------------------------------------------------------

/**
 * A minimal registry of a cardholder's active approvals. VIC holds the source of truth; this is your
 * app's view so the person can see and revoke what their agent may spend.
 */
export class AgentWallet {
  private readonly instructions = new Map<string, PurchaseInstruction>();

  constructor(private readonly vic: VicClient, private readonly payloads: VicPayloads) {}

  add(instruction: PurchaseInstruction): void {
    this.instructions.set(instruction.instructionId, instruction);
  }

  list(): PurchaseInstruction[] {
    return [...this.instructions.values()];
  }

  /** Let the cardholder revoke an approval at any time. */
  async revoke(instructionId: string, reason = "Revoked by cardholder"): Promise<void> {
    await this.vic.cancelPurchaseInstruction(instructionId, this.payloads.cancel({ reason }));
    this.instructions.delete(instructionId);
  }

  /** Lower (never silently raise) the cap on an approval. Raising it needs fresh cardholder approval. */
  async lowerCap(
    instructionId: string,
    newMaxAmountMinor: number,
    owner: { consumerId: string; tokenId: string },
  ): Promise<void> {
    const current = this.instructions.get(instructionId);
    if (!current) throw new Error(`Unknown instruction ${instructionId}`);
    if (newMaxAmountMinor > current.mandate.maxAmountMinor) {
      throw new VicError("Raising a cap requires new cardholder approval.", "MANDATE_EXCEEDED");
    }
    const mandate = { ...current.mandate, maxAmountMinor: newMaxAmountMinor };
    await this.vic.updatePurchaseInstruction(
      instructionId,
      this.payloads.purchaseInstruction({ ...owner, mandate }),
    );
    this.instructions.set(instructionId, { ...current, mandate });
  }
}

// ---------------------------------------------------------------------------------------------
// 4. Handle webhooks (generic, verify-then-process pattern)
// ---------------------------------------------------------------------------------------------

/**
 * Verifies an HMAC-SHA256 signed webhook, then hands the parsed event to `handle`. This is a generic
 * pattern: the actual event names, header names and signing scheme come from your Visa or processor
 * configuration. VIC responses also carry `pendingEvents` you can poll instead.
 *
 * Uses the Web Crypto API (Node 18+, Deno, Workers, browsers).
 */
export async function handleWebhook(
  rawBody: string,
  signatureHex: string,
  secret: string,
  handle: (event: { type: string; instructionId?: string; [key: string]: unknown }) => Promise<void>,
): Promise<void> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["verify"]);
  const sig = hexToBytes(signatureHex);
  const ok = sig !== null && await crypto.subtle.verify("HMAC", key, sig, enc.encode(rawBody));
  if (!ok) throw new VicError("Webhook signature did not verify.", "WEBHOOK_REJECTED");
  const event = JSON.parse(rawBody) as { type?: unknown };
  if (typeof event.type !== "string") throw new VicError("Webhook has no event type.", "WEBHOOK_REJECTED");
  await handle(event as { type: string });
}

function hexToBytes(hex: string): Uint8Array | null {
  if (!/^(?:[0-9a-fA-F]{2})+$/.test(hex)) return null;
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  return out;
}

// ---------------------------------------------------------------------------------------------
// 5. Metered billing ("tab" accounts) — a usage pattern, not a Visa product
// ---------------------------------------------------------------------------------------------

/**
 * Accumulates small usage charges (for example per-report fees from a SaaS marketing tool) and settles
 * them as ONE payment per period, inside a recurring instruction the cardholder approved. This keeps the
 * number of card transactions low and every charge within the approved cap.
 */
export class MeteredTab {
  private readonly lines: Array<{ description: string; amountMinor: number; at: string }> = [];

  constructor(private readonly instruction: PurchaseInstruction) {}

  /** Adds a usage line. Refuses anything that would push the period total over the approved cap. */
  addUsage(description: string, amountMinor: number, at: Date = new Date()): void {
    if (!Number.isInteger(amountMinor) || amountMinor <= 0) throw new Error("amountMinor must be a positive integer");
    if (this.totalMinor() + amountMinor > this.instruction.mandate.maxAmountMinor) {
      throw new VicError("This usage would exceed the approved monthly cap.", "MANDATE_EXCEEDED");
    }
    this.lines.push({ description, amountMinor, at: at.toISOString() });
  }

  totalMinor(): number {
    return this.lines.reduce((sum, line) => sum + line.amountMinor, 0);
  }

  /** Settles the period with one payment, then clears the tab. Itemized lines go on the receipt. */
  async settle(
    vic: VicClient,
    payloads: VicPayloads,
    tokenId: string,
    periodId: string,
    checkout: (credentials: TransactionCredentials, amountMinor: number) => Promise<CheckoutOutcome>,
  ): Promise<{ outcome: CheckoutOutcome; amountMinor: number; lines: number }> {
    const amountMinor = this.totalMinor();
    if (amountMinor === 0) return { outcome: "cancelled", amountMinor: 0, lines: 0 };
    const outcome = await initiatePayment(vic, payloads, {
      tokenId,
      instruction: this.instruction,
      purchase: { merchantUrl: this.instruction.mandate.merchantUrl, amountMinor, currency: this.instruction.mandate.currency },
      transactionReferenceId: `${this.instruction.instructionId}:${periodId}`, // stable per period: safe to retry
      checkout: (credentials) => checkout(credentials, amountMinor),
    });
    const lines = this.lines.length;
    if (outcome === "approved") this.lines.length = 0;
    return { outcome, amountMinor, lines };
  }
}
