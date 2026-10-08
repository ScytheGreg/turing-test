const test = require("node:test");
const assert = require("node:assert/strict");

const {
    getDisplayConfig,
    getMessageLabel,
} = require("../frontend/display/config.js");


test("uses Alice and Bob by default", () => {
    assert.deepEqual(getDisplayConfig(), {
        left: "alice",
        right: "bob",
        leftName: "ALICE",
        rightName: "BOB",
    });
});

test("accepts sessions and display names from the URL", () => {
    const config = getDisplayConfig(
        "?left=bob&leftName=Kasia&right=ALICE&rightName=Tomek"
    );

    assert.deepEqual(config, {
        left: "bob",
        right: "alice",
        leftName: "Kasia",
        rightName: "Tomek",
    });
});

test("decodes names and falls back for blank names", () => {
    const config = getDisplayConfig("?leftName=Kasia%20Nowak&rightName=%20");

    assert.equal(config.leftName, "Kasia Nowak");
    assert.equal(config.rightName, "BOB");
});

test("ignores unknown sessions and prevents duplicate panels", () => {
    assert.deepEqual(getDisplayConfig("?left=unknown&right=alice"), {
        left: "alice",
        right: "bob",
        leftName: "ALICE",
        rightName: "BOB",
    });

    assert.deepEqual(getDisplayConfig("?left=bob&right=bob"), {
        left: "bob",
        right: "alice",
        leftName: "BOB",
        rightName: "ALICE",
    });
});

test("uses short labels for questions and answers", () => {
    assert.equal(getMessageLabel("user_message"), "Pytanie");
    assert.equal(getMessageLabel("assistant_message"), "Odpowiedź");
    assert.equal(getMessageLabel("human_reply"), "Odpowiedź");
});
