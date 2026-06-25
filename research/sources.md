# Sources

Curated source index for lead-nurture RAG bot research. Keep entries concise and tied to what they support.

## RAG and evaluation methodology

- RAGAS metrics — https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/ — RAG evaluation categories.
- TruLens RAG triad — https://www.trulens.org/getting_started/core_concepts/rag_triad/ — context relevance, groundedness, answer relevance framing.
- DeepEval metrics — https://deepeval.com/docs/metrics-introduction — LLM app evaluation patterns.
- BEIR — https://github.com/beir-cellar/beir — retrieval benchmark framework reference.
- MS MARCO on Hugging Face — https://huggingface.co/datasets/mteb/msmarco — retrieval dataset reference, not directly lead-nurture-specific.
- scikit-learn nDCG — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html — retrieval ranking metric.
- scikit-learn average precision — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html — ranking/classification metric.
- Google ML classification metrics — https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall — precision/recall explanation for score/action classification.

## Compliance and email constraints

- FTC CAN-SPAM compliance guide — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — US commercial email requirements.
- Google sender requirements — https://support.google.com/a/answer/81126 — SPF/DKIM/DMARC, spam rate, unsubscribe, TLS, bulk sender requirements.
- Yahoo sender best practices — https://senders.yahooinc.com/best-practices/ — sender authentication, unsubscribe, complaint/bounce expectations.
- UK ICO PECR email marketing guidance — https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/electronic-mail-marketing/ — consent and B2B/B2C marketing email constraints.
- GDPR regulation text — https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng — objection to direct marketing/profiling and automated decision-making safeguards.
- ICO automated decision-making guidance — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/automated-decision-making-and-profiling/ — human intervention/contestation guidance.
- Canada CASL — https://ised-isde.canada.ca/site/canada-anti-spam-legislation/en — commercial electronic message consent regime.
- FCC robocalls/texts guide — https://www.fcc.gov/consumers/guides/stop-unwanted-robocalls-and-texts — SMS/call expansion risk.
- California CCPA — https://oag.ca.gov/privacy/ccpa — privacy rights context.
- Twilio SendGrid Event Webhook reference — https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event — official event categories for delivery and engagement events, including bounces, spam reports, and unsubscribes.
- Postmark Webhooks overview — https://postmarkapp.com/developer/webhooks/webhooks-overview — official webhook mechanism for bounce, delivery, click/open, spam complaint, subscription-change, and inbound events.
- Amazon SES event notifications — https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html — official bounce/complaint notification and sending-event monitoring options.
- Mailgun tracking messages docs — https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/ — official tracking docs for unsubscribes, spam complaints, failures, deliveries, webhooks, and events.

## Competitive landscape: sales/GTM platforms

- Apollo — https://www.apollo.io/ ; https://www.apollo.io/pricing
- Clay — https://www.clay.com/ ; https://www.clay.com/pricing
- ZoomInfo — https://www.zoominfo.com/pricing
- Cognism — https://www.cognism.com/pricing
- Seamless.AI — https://seamless.ai/pricing
- Demandbase — https://www.demandbase.com/
- Common Room — https://www.commonroom.io/pricing/
- Unify — https://www.unifygtm.com/pricing
- Outreach — https://www.outreach.ai ; https://www.outreach.ai/pricing
- Salesloft — https://www.salesloft.com/ ; https://www.salesloft.com/pricing
- Regie.ai — https://www.regie.ai/
- Instantly — https://instantly.ai/pricing
- Smartlead — https://www.smartlead.ai/pricing
- lemlist — https://www.lemlist.com/pricing
- Salesforce Sales Cloud — https://www.salesforce.com/sales/pricing/
- HubSpot Sales Hub — https://www.hubspot.com/pricing/sales
- Close CRM — https://close.com/pricing

## Competitive landscape: local/private RAG and build substrates

- Onyx — https://onyx.app/ ; https://onyx.app/pricing ; https://github.com/onyx-dot-app/onyx
- AnythingLLM — https://anythingllm.com/ ; https://github.com/Mintplex-Labs/anything-llm
- PrivateGPT — https://github.com/zylon-ai/private-gpt
- LangChain — https://github.com/langchain-ai/langchain
- LlamaIndex — https://github.com/run-llama/llama_index

## Integration architecture: email/CRM APIs

- SendGrid Inbound Parse Webhook — https://www.twilio.com/docs/sendgrid/for-developers/parsing-email/setting-up-the-inbound-parse-webhook — primary source for parsing inbound emails into webhooks before normalization.
- Postmark inbound processing — https://postmarkapp.com/developer/user-guide/inbound — primary source for inbound email delivered to applications via formatted JSON webhooks.
- Mailgun receiving messages via HTTP/routes — https://documentation.mailgun.com/docs/mailgun/user-manual/receive-forward-store/receive-http — primary source for routing received messages to HTTP endpoints and parsed payload fields.
- Close developer portal — https://developer.close.com/ — primary source for REST API use cases around leads, contacts, activities, custom data, webhooks, and event logs.
- HubSpot CRM contacts/objects/webhooks docs — https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/guide ; https://developers.hubspot.com/docs/api-reference/crm-objects-v3/guide ; https://developers.hubspot.com/docs/api/webhooks — reachable but JavaScript-heavy/static extraction was insufficient in the 2026-06-24 integration-architecture run.
- Salesforce REST API intro — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm — attempted in the 2026-06-24 integration-architecture run; blocked by HTTP 403 from this environment.

## Product wedge and customer discovery

- Apollo pricing/product page — https://www.apollo.io/pricing — primary source for Apollo positioning around sales intelligence, prospecting, inbound lead qualification, enrichment, AI assistant, CRM/export workflows, and free sign-up path.
- Close pricing/product page — https://close.com/pricing — primary source for Close positioning around CRM, email/calling/SMS, workflows, lead pipeline management, Chloe AI sales agent, business-count claim, imports, API access, and event log.
- HubSpot state-of-sales attempted URL — https://www.hubspot.com/state-of-sales — attempted in the 2026-06-24 product-wedge run; returned HTTP 404/static fallback from this environment, so no report-specific claims were used.
- HubSpot public site fallback from attempted page — https://www.hubspot.com/state-of-sales — same attempted URL surfaced general HubSpot product navigation text for Smart CRM, small-business/startup packaging, Breeze AI agents, and AI prospecting agent, but treat as dynamic/fallback context rather than a stable report citation.
- AnythingLLM product page — https://anythingllm.com/ — primary source for packaging local/offline/private document chat and local defaults for LLM/embedder/vector DB/storage/agents.
- Y Combinator Startup Library — https://www.ycombinator.com/library — reachable methodology background for startup/customer-discovery material; the previously known direct “talk to users” slug returned 404 in this environment.
- Y Combinator broken slug — https://www.ycombinator.com/library/6g-how-to-talk-to-users — returned HTTP 404 on 2026-06-24; logged as a blocked/broken source, not used for substantive claims.

## UX / rubric inspiration

- Nielsen Norman Group usability heuristics — https://www.nngroup.com/articles/ten-usability-heuristics/ — useful for human-review queue and response review UX rubric.
