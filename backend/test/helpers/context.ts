export interface TestContext {
  env: Record<string, unknown>;
}

export async function createTestContext(): Promise<TestContext> {
  return { env: {} };
}
