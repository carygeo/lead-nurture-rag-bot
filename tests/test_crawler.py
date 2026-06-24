from lead_nurture_rag.crawler import CampaignConfig, crawl_campaign, extract_document


def test_campaign_crawler_discovers_allowed_links_and_skips_noise(monkeypatch):
    pages = {
        "https://acme.test/": """
        <html><head><title>Acme AI</title></head><body>
          <main>AI for construction payment applications.</main>
          <a href="/solutions/pay-apps">Solutions</a>
          <a href="/privacy">Privacy</a>
          <a href="https://external.test/nope">External</a>
        </body></html>
        """,
        "https://acme.test/solutions/pay-apps": """
        <html><head><title>Pay App Validation</title></head><body>
          <main>Reduce missing lien waivers and payment application risk for project teams.</main>
        </body></html>
        """,
    }

    class Response:
        def __init__(self, url):
            self.text = pages[url]
            self.status_code = 200
            self.headers = {"content-type": "text/html"}
            self.url = url

        def raise_for_status(self):
            return None

    def fake_get(url, timeout, headers):
        assert url in pages
        return Response(url)

    monkeypatch.setattr("lead_nurture_rag.crawler.requests.get", fake_get)
    config = CampaignConfig(
        company_name="Acme",
        root_url="https://acme.test",
        allowed_domains=["acme.test"],
        seed_pages=["https://acme.test/"],
        crawl_depth=1,
        max_pages=5,
    )

    docs = crawl_campaign(config)

    assert [doc.url for doc in docs] == [
        "https://acme.test/",
        "https://acme.test/solutions/pay-apps",
    ]
    assert docs[1].metadata["page_type"] == "solution"
    assert "payment_application_validation" in docs[1].metadata["topics"]


def test_extract_document_uses_metadata_when_rendered_body_is_sparse():
    html = """
    <html>
      <head>
        <title>Supernews — Visual, Bite-Sized News</title>
        <meta name="description" content="AI-powered news curation that delivers the stories that matter.">
        <meta property="og:description" content="AI summaries, weather, quizzes, and live reactions for how you read.">
        <script type="application/ld+json">
          {"@type":"Organization","name":"Supernews","url":"https://getsupernews.com/"}
        </script>
      </head>
      <body><div id="root">Edit with</div><script src="/assets/app.js"></script></body>
    </html>
    """

    doc = extract_document("https://getsupernews.com/", html, "Supernews")

    assert "AI-powered news curation" in doc.text
    assert "AI summaries" in doc.text
    assert "Supernews" in doc.text
    assert "Edit with" not in doc.text
