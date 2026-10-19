"""Reproducible local size benchmark; measures characters, not model tokens."""
from promptpilot.core import build_prompt, compare_text, compact_text, create_handoff


def main():
    prompt_args = {
        "task": "Write a Facebook post announcing a new customer gift service.",
        "requirements": "Vietnamese; warm professional tone; include 3 relevant hashtags; do not invent prices or contact details.",
        "source_material": "Service: fresh flowers, fruit baskets, trend gifts, artistic money bouquets, custom designs.\n\nService: fresh flowers, fruit baskets, trend gifts, artistic money bouquets, custom designs.",
        "output_limit": "Under 120 words. Return only the post.",
    }
    old_prompt = build_prompt(**prompt_args, compact=False)
    new_prompt = build_prompt(**prompt_args, compact=True)
    print("PROMPT BUILDER (verbose vs compact)")
    print(compare_text(old_prompt, new_prompt))

    noisy = ("Meeting notes\nAction: publish draft Friday\nMeeting notes\n\n\n"
             "Action: publish draft Friday\nOwner: Linh\nOwner: Linh\nDeadline: Friday")
    compacted = compact_text(noisy)
    print("TEXT CLEANUP (formatting + exact duplicate lines)")
    print(compare_text(noisy, compacted))

    handoff_args = {"summary": "Project: customer gift page; draft description completed.",
                    "decisions": "Keep separate from funeral business branding.",
                    "open_questions": "Need final page name.", "next_steps": "Prepare cover image brief."}
    print("HANDOFF (verbose vs compact)")
    print(compare_text(create_handoff(**handoff_args, compact=False), create_handoff(**handoff_args, compact=True)))

if __name__ == "__main__":
    main()
