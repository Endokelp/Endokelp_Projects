/**
 * Pauses `git push` so you run the pre-push vibe pass (see .cursor/pre-push.md).
 * Requires Node on PATH. If stdin isn't JSON (older Cursor), allows the command.
 */
const readStdin = () =>
  new Promise((resolve) => {
    let buf = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (c) => {
      buf += c;
    });
    process.stdin.on("end", () => resolve(buf));
  });

readStdin().then((raw) => {
  let input = {};
  try {
    input = JSON.parse(raw || "{}");
  } catch {
    console.log(JSON.stringify({ permission: "allow" }));
    process.exit(0);
    return;
  }
  const command = String(input.command || "").toLowerCase();
  const isGitPush = /\bgit\b/.test(command) && /\bpush\b/.test(command);
  if (isGitPush) {
    console.log(
      JSON.stringify({
        permission: "ask",
        user_message:
          "Pre-push: run the vibe pass in .cursor/pre-push.md (yourself or spawn an agent with that brief). Then push again.",
        agent_message:
          "Before git push: follow .cursor/pre-push.md — run the detective checklist or a subagent with that prompt, fix HIGH issues, then retry push.",
      }),
    );
    process.exit(0);
    return;
  }
  console.log(JSON.stringify({ permission: "allow" }));
  process.exit(0);
});
