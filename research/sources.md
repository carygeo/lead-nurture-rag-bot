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

## UX / rubric inspiration

- Nielsen Norman Group usability heuristics — https://www.nngroup.com/articles/ten-usability-heuristics/ — useful for human-review queue and response review UX rubric.
