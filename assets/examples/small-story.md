# Add A Saved Filter

Users want to save one search filter on the projects page so they can return to the same view in a later browser session.

Acceptance criteria:

- A user can save the current project status filter.
- A user can clear the saved filter.
- The default view is unchanged for users without a saved filter.
- The saved filter uses browser-local persistence for the starter demo; no server-side persistence is required.

Notes:

- Product is unsure whether saved filters should sync across devices. Treat that as out of scope for the first slice.
- Module-level in-memory state is not enough for this story because it does not survive reloads or later browser sessions.
