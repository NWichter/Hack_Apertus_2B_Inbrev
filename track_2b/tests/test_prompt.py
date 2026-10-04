from inbrev import prompt


def test_p3_is_default_and_p2_stays_reproducible():
    assert prompt.PROMPT_VERSION == "p3"
    p2, p3 = prompt.system_prompt("p2"), prompt.system_prompt("p3")
    assert "copy or transfer of medical records" not in p2
    assert "copy or transfer of medical records" in p3
    assert "{" not in p2.split("OUTPUT:")[0] and "{" not in p3.split("OUTPUT:")[0]
    for route in ("report_received", "certificate_request", "referral_in", "other"):
        assert f"- {route}:" in p2 and f"- {route}:" in p3
    safety_rule = next(l for l in p2.splitlines() if l.startswith("- safety_flag is true"))
    assert safety_rule in p3
