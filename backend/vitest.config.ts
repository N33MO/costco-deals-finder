import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'happy-dom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'test/', '**/*.d.ts', '**/*.config.ts', '.eslintrc.cjs'],
      include: ['src/**/*.ts'],
      all: true,
      thresholds: {
        statements: 0,
        branches: 0,
        functions: 0,
        lines: 0,
      },
    },
    include: ['test/**/*.test.ts'],
    globals: true,
    reporters: ['default', 'html'],
    outputFile: {
      html: './coverage/test-report.html',
    },
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 10000,
  },
});
