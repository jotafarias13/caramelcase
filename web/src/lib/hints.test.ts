import { describe, expect, it } from "vitest";
import { activeHint, dismissHint, offerHint, resetHints } from "./hints";

describe("hints", () => {
  it("shows nothing while no hint has its place on screen", () => {
    expect(activeHint()).toBeNull();
  });

  it("shows one hint at a time, in the order of the list", () => {
    offerHint("topics");
    offerHint("streak");
    expect(activeHint()).toBe("streak");

    dismissHint("streak", { advance: true });
    expect(activeHint()).toBe("topics");

    dismissHint("topics", { advance: true });
    expect(activeHint()).toBeNull();
  });

  it("stops showing a hint whose place left the screen", () => {
    const leave = offerHint("xp");
    offerHint("rating");
    expect(activeHint()).toBe("xp");

    leave();
    expect(activeHint()).toBe("rating");
  });

  it("goes quiet after a hint closed any other way, until a screen arrives", () => {
    offerHint("streak");
    offerHint("topics");

    dismissHint("streak", { advance: false });
    expect(activeHint()).toBeNull();

    offerHint("subject");
    expect(activeHint()).toBe("topics");
  });

  it("remembers on the device what was shown", () => {
    offerHint("xp");
    dismissHint("xp", { advance: true });
    expect(localStorage.getItem("caramelcase.hints")).toBe('["xp"]');

    // The page is loaded again.
    resetHints();
    offerHint("xp");
    offerHint("rating");
    expect(activeHint()).toBe("rating");
  });

  it("starts empty when what is stored cannot be read", () => {
    localStorage.setItem("caramelcase.hints", "not json");
    offerHint("xp");
    expect(activeHint()).toBe("xp");

    resetHints();
    localStorage.setItem("caramelcase.hints", '{"xp": true, "unknown": 1}');
    offerHint("xp");
    expect(activeHint()).toBe("xp");
  });
});
