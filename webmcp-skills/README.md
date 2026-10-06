# WebMCP skills

Reusable WebMCP tool definitions for marketing services. Each file is one tool: `name`, `description`,
`inputSchema`, `outputSchema`, `annotations`, and fictional `examples`.

| File | Tool | Side effects |
| --- | --- | --- |
| [marketing-discovery.json](marketing-discovery.json) | `discover_marketing_services` | None (read-only) |
| [campaign_optimization.json](campaign_optimization.json) | `optimize_campaign` | None: recommendations only |
| [analytics_retrieval.json](analytics_retrieval.json) | `retrieve_campaign_analytics` | None: aggregates only |
| [pricing_comparison.json](pricing_comparison.json) | `compare_pricing` | None: your own offers only |

To use one: copy it, replace the enums and examples with your own, remove `$comment` and `examples` if your
WebMCP library rejects extra keys, and register it with `document.modelContext.registerTool` plus an
`execute` handler. See the [implementation guide](../IMPLEMENTATION-GUIDE.md).

All example data is fictional (ILLUSTRATIVE). WebMCP is a draft standard:
[webmachinelearning.github.io/webmcp](https://webmachinelearning.github.io/webmcp/).
