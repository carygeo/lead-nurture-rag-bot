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
- Repo `KnowledgeChunk` model — https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/models.py — primary repo source for fixture row shape (`id`, `source`, `text`, `metadata`).
- Repo TF-IDF retriever — https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/retriever.py — primary repo source for local retrieval behavior and `KnowledgeBase.search` smoke-test harness.
- Repo metadata categorizer — https://github.com/carygeo/lead-nurture-rag-bot/blob/main/src/lead_nurture_rag/categorizer.py — primary repo source for searchable metadata fields mirrored in the canned KB fixture.
- Repo executable research smoke eval — https://github.com/carygeo/lead-nurture-rag-bot/blob/main/scripts/research_smoke_eval.py — versioned local fixture validation, TF-IDF retrieval smoke metrics, and deterministic observation/scoring baseline metrics using the repo's current analyzer and scoring rules.

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
- ComplianceGate schema slice sources — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://support.google.com/a/answer/81126 ; https://senders.yahooinc.com/best-practices/ ; https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event ; https://postmarkapp.com/developer/webhooks/webhooks-overview ; https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html ; https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/ — 2026-06-25 source set for proposed local `ComplianceGate` result schema, ambiguous opt-out fixture, and stale-approval fixture. Exact schema names are design hypotheses; cited constraints support opt-out, footer, provider event, and bounce/complaint guardrails.
- ComplianceGate executable-invariant slice — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://support.google.com/a/answer/81126 ; https://senders.yahooinc.com/best-practices/ ; https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event ; https://postmarkapp.com/developer/webhooks/webhooks-overview ; https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html ; https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/ — all returned HTTP 200 on 2026-06-25 in the scheduled run. Used to justify fixture invariant checks that opt-out, provider complaint/bounce/unsubscribe, missing unsubscribe URL/postal address, and stale human review should be machine-readable non-send blockers. Local invariant names are design hypotheses, not vendor/legal standards.
- ComplianceGate minimal implementation slice — https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://support.google.com/a/answer/81126 ; https://senders.yahooinc.com/best-practices/ ; https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event ; https://postmarkapp.com/developer/webhooks/webhooks-overview ; https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html ; https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/ — all returned HTTP 200 on 2026-06-25 02:56 EDT. Used as source basis for a conservative local `ComplianceGate` pre-send/pre-draft implementation; implementation behavior is a product guardrail and not legal advice or deliverability evidence.

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

## Differentiation and demo strategy

- Salesforce Agentforce — https://www.salesforce.com/agentforce/ — primary source for broad enterprise AI-agent positioning; fetched page described humans, applications, AI agents, and data, and an SDR example that engages prospects 24/7, handles questions/objections, and schedules meetings from CRM/external data.
- HubSpot Breeze AI — https://www.hubspot.com/products/artificial-intelligence — primary source for CRM-native AI-agent positioning; fetched page described AI tools/agents built into CRM, a prospecting agent for personalized outreach strategies, and next-best-steps/talking-points/ready-to-send email-draft capabilities.
- Outreach platform — https://www.outreach.ai/platform — primary source for agentic AI revenue platform positioning across sales engagement, deal management, forecasting, and coaching.
- Apollo pricing/product navigation — https://www.apollo.io/pricing — primary source for Apollo positioning around sales intelligence, lead generation, email outreach, prospecting, inbound conversion, and CRM export/sync.
- Apollo broken AI-sales-agent URL — https://www.apollo.io/product/ai-sales-agent — returned HTTP 404 on 2026-06-24; logged as a blocked/broken source and not used for product-specific claims.
- AnythingLLM product and GitHub — https://anythingllm.com/ ; https://github.com/Mintplex-Labs/anything-llm — primary sources for local/offline document chat, AI agents, private operation, and source-citation capability.

## Competitive matrix: AI SDR / conversational lead engagement

- 11x home page — https://www.11x.ai/ — primary source for digital-AI-worker positioning, outbound/inbound qualification, lead nurture/reactivation, website visitors, meeting scheduling, CRM/Slack/G2 integrations, and API references. The attempted pricing URL https://www.11x.ai/pricing returned 404 on 2026-06-24.
- Artisan home page and pricing page — https://www.artisan.co/ ; https://www.artisan.co/pricing — primary sources for AI BDR / AI employee positioning, Ava outbound automation, lead finding/prioritization, campaign execution, reply/objection handling, meeting booking, human-escalation rules, and trial-credit language. Exact paid tier pricing was not extracted from static text.
- Salesloft Drift platform and Drift redirect — https://www.drift.com/products/drift-engage/ ; https://www.salesloft.com/platform/drift — primary sources for Drift redirect behavior, AI chat agents, website visitors to pipeline, and revenue-orchestration positioning. Salesloft pricing page https://www.salesloft.com/pricing was reachable but exact public prices were not extracted from static text.
- Pipedrive AI Sales Assistant — https://www.pipedrive.com/en/features/ai-sales-assistant — primary source for CRM-native AI sales assistant positioning around analyzing actions/past performance, suggesting actions, notifications, and progress updates. Pipedrive pricing URL https://www.pipedrive.com/en/pricing returned an “Attention Required”/403-style page on 2026-06-24.
- Blocked/broken AI-SDR adjacent sources — https://www.6sense.com/platform/revenue-ai/ returned Cloudflare/403; https://www.lusha.com/pricing/ returned browser-check/403; https://reply.io/ returned Cloudflare/403 and https://reply.io/ai-sales-agents/ returned 404/static fallback; https://www.qualified.com/products/piper returned 404/Page Not Found. These are logged as blocked/dynamic findings, not product-evidence sources.

## UX / rubric inspiration

- Nielsen Norman Group usability heuristics — https://www.nngroup.com/articles/ten-usability-heuristics/ — useful for human-review queue and response review UX rubric.
