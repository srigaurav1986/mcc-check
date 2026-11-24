// Run from anywhere: node tests/web/test_web_logic.js
// Loads the pure logic block from web/index.html and checks it with a mock fetch.
const fs = require("fs");
const path = require("path");
const file = path.join(__dirname, "..", "..", "web", "index.html");
const html = fs.readFileSync(file, "utf8");
const logic = html.split("/*LOGIC_START*/")[1].split("/*LOGIC_END*/")[0];
const L = new Function(logic + "; return {suggest, confidence, expectedMdr, RULES, aiSuggest, parseAiReply, redact, buildAiMessages, BY_CODE, MCC_TABLE};")();

let fails = 0;
const check = (cond, msg) => { console.log((cond ? "ok: " : "FAIL: ") + msg); if (!cond) fails++; };
const mockFetch = (body, status = 200) => {
  const f = async (url, opts) => { f.calls.push({url, opts}); return {ok: status < 400, status, json: async () => body}; };
  f.calls = []; return f;
};

(async () => {
  // MCC suggestions
  check(L.suggest("श्री जी हौज़री")[0].code === "5651", "hosiery maps to 5651");
  check(L.suggest("darzi tailor")[0].code === "5691", "tailor maps to 5691");
  check(L.suggest("school uniform")[0].code === "5137", "uniform maps to 5137");
  check(L.MCC_TABLE.length === 32, "table has 32 codes");

  // MDR rule
  check(L.expectedMdr(2000, L.RULES.upi_p2m) === 0, "₹2,000 is zero MDR");
  check(L.expectedMdr(3000, L.RULES.upi_p2m) === 12, "₹3,000 gives ₹12");
  check(L.expectedMdr(90000, L.RULES.upi_p2m) === 300, "cap ₹300 applies");

  // AI: consent gate
  let f = mockFetch({});
  try { await L.aiSuggest("x", {consent: false, apiKey: "k", provider: "gemini"}, f); check(false, "consent required"); }
  catch (e) { check(f.calls.length === 0, "no consent -> no network call"); }

  // AI: Gemini request shape and redaction
  f = mockFetch({candidates: [{finishReason: "STOP", content: {parts: [{text: '{"code":"5651","confidence":0.8,"reason_hi":"कपड़े"}'}]}}]});
  const r = await L.aiSuggest("श्री जी हौज़री, 98765 43210", {consent: true, apiKey: "GKEY", provider: "gemini"}, f);
  check(f.calls[0].url.includes("generativelanguage.googleapis.com"), "gemini endpoint used");
  check(f.calls[0].opts.headers["x-goog-api-key"] === "GKEY", "gemini key in header, not URL");
  check(!f.calls[0].opts.body.includes("98765"), "phone-like number redacted before send");
  check(r.code === "5651", "gemini reply parsed");

  // AI: invalid code rejected
  check(L.parseAiReply('{"code":"9999","confidence":0.9,"reason_hi":"x"}').code === null, "code outside list rejected");

  // AI: truncated reply
  f = mockFetch({candidates: [{finishReason: "MAX_TOKENS", content: {parts: [{text: '{"'}]}}]});
  try { await L.aiSuggest("x", {consent: true, apiKey: "k", provider: "gemini"}, f); check(false, "truncation reported"); }
  catch (e) { check(e.message.includes("रुक गया"), "truncated reply gives clear message"); }

  console.log(fails ? "FAILURES: " + fails : "ALL WEB LOGIC TESTS PASSED");
  process.exitCode = fails ? 1 : 0;
})();
