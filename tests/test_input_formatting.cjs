const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../static/script.js"), "utf8");
const helpers = {};
vm.runInNewContext(source.slice(source.indexOf("function parseClock("), source.indexOf("class SmartTime")), helpers);
vm.runInNewContext(source.slice(source.indexOf("function normalizeLeadPhone("), source.indexOf("function setupLeadWizard(")), helpers);

for (const [input, expected] of [
    ["90 123 45 67", "+998901234567"],
    ["+998 (90) 123-45-67", "+998901234567"],
    ["998901234567", "+998901234567"],
    ["+1 (202) 555-0123", "+12025550123"],
    ["", null], ["90 123", null], ["90abc4567", null], ["++998901234567", null],
]) assert.equal(helpers.normalizeLeadPhone(input), expected);

for (const [input, expected] of [["0", "00:00"], ["9", "09:00"], ["930", "09:30"], ["1430", "14:30"], ["23:59", "23:59"], ["14:3", "14:03"]]) {
    assert.equal(helpers.parseClock(input), expected);
}
for (const input of ["", "24", "2400", "12:60", "02:00 PM", "14:3a", "-1:00"]) assert.equal(helpers.parseClock(input), null);

for (const [input, raw, displayed] of [
    ["1250000", "1250000", "1 250 000"],
    ["1 250 000,50", "1250000.50", "1 250 000,50"],
    ["1\u202f250\u00a0000.50", "1250000.50", "1 250 000,50"],
    ["0001250,5", "1250.5", "1 250,50"],
    ["0", "0", "0"],
    ["", "", ""],
    [".75", "0.75", "0,75"],
    ["999999999999.99", "999999999999.99", "999 999 999 999,99"],
]) {
    assert.equal(helpers.canonicalMoney(input), raw);
    assert.equal(helpers.formatMoneyInput(input, true), displayed);
    assert.equal(helpers.canonicalMoney(displayed), raw === "1250.5" ? "1250.50" : raw);
}
for (const input of ["-1", "1,234", "12a34", "1,2,3", "1e6", "1000000000000", "."]) assert.equal(helpers.canonicalMoney(input), null);
assert.equal(helpers.formatMoneyInput("1234,"), "1 234,");
assert.equal(helpers.formatMoneyInput("-1200", true), "-1200");

for (const [start, months, expected] of [
    ["2026-11-03", 6, "2027-05-03"],
    ["2026-01-31", 1, "2026-02-28"],
    ["2028-01-31", 1, "2028-02-29"],
    ["2024-02-29", 12, "2025-02-28"],
    ["2026-12-31", 1, "2027-01-31"],
    ["2026-02-31", 6, null],
    ["2026-11-03", null, null],
    ["", 6, null],
    ["9999-12-01", 1, null],
]) assert.equal(helpers.suggestGroupEnd(start, months), expected);

console.log("Time, money, course end-date suggestions, and lead phone formatting passed.");
