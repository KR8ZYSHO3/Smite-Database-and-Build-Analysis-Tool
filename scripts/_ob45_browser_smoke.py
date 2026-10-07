"""OB45 browser smoke: patch stamp, Nike/Hel on Builds, Counter, Item guide."""
from __future__ import annotations

from playwright.sync_api import expect, sync_playwright

BASE = "http://127.0.0.1:8765/"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        page.wait_for_function(
            "() => document.querySelector('#ctr-god-list')?.options?.length > 10",
            timeout=60000,
        )
        hc = page.locator("#help-close")
        if hc.count() and hc.is_visible():
            hc.click()

        # Patch / last-updated should mention OB45 or Open Beta 45
        stamp = page.locator("#meta-stamp, .meta-stamp, footer, #last-updated, .last-updated").first
        body_text = page.inner_text("body")
        assert "Open Beta 45" in body_text or "OB45" in body_text or "Goddess Of Victory" in body_text, (
            "patch stamp missing OB45"
        )

        # Builds: role pills + search
        page.locator('nav.tabs button.tab-btn[data-tab="builds"]').click()
        expect(page.locator("#panel-builds")).to_be_visible()
        page.wait_for_selector("#role-pills button, #role-pills .pill", timeout=15000)

        def pick_role(label: str) -> None:
            pill = page.locator("#role-pills button, #role-pills .pill", has_text=label).first
            if pill.count():
                pill.click()
                page.wait_for_timeout(350)

        def find_god(name: str):
            search = page.locator("#build-god-search")
            search.fill(name)
            page.wait_for_timeout(450)
            return page.locator("details.god-build-card", has_text=name).first

        pick_role("Support")
        hel = find_god("Hel")
        expect(hel).to_be_visible(timeout=15000)
        if hel.get_attribute("open") is None:
            hel.locator("summary.build-expand-summary").click()
            page.wait_for_timeout(300)
        expect(hel.locator(".buy-row").first).to_be_visible()
        hel_text = hel.inner_text()
        assert "Lotus Sickle" in hel_text or "Asclepius" in hel_text, hel_text[:400]

        pick_role("Solo")
        nike = find_god("Nike")
        expect(nike).to_be_visible(timeout=15000)

        pick_role("Support")
        aph = find_god("Aphrodite")
        expect(aph).to_be_visible(timeout=15000)
        if aph.get_attribute("open") is None:
            aph.locator("summary.build-expand-summary").click()
            page.wait_for_timeout(300)
        aph_text = aph.inner_text()
        assert "Lotus Sickle" in aph_text, aph_text[:500]
        assert "Asclepius" in aph_text, aph_text[:500]

        # Counter tool still loads gods including new ones
        page.locator('nav.tabs button.tab-btn[data-tab="counter"]').click()
        page.wait_for_timeout(300)
        expect(page.locator("#panel-counter")).to_be_visible()
        opts = page.evaluate(
            """() => Array.from(document.querySelector('#ctr-god-list')?.options || []).map(o => ({
              text: (o.textContent || o.label || o.value || '').trim(),
              value: (o.value || '').trim()
            }))"""
        )
        labels = [o["text"] or o["value"] for o in opts]
        assert any("Hel" in o for o in labels), labels[:30]
        assert any("Nike" in o for o in labels), labels[:30]

        # Meta / item guide
        page.locator('nav.tabs button.tab-btn[data-tab="meta"]').click()
        page.wait_for_timeout(400)
        assert "Heartwood" in page.inner_text("body") or page.locator("#tier-board, .tier-board").count()

        print("OB45 BROWSER SMOKE OK")
        print("  gods in counter:", len(opts))
        print("  stamp sample:", body_text[body_text.find("Open Beta") : body_text.find("Open Beta") + 40] if "Open Beta" in body_text else "n/a")
        browser.close()


if __name__ == "__main__":
    main()
