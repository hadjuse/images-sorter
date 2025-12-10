module.exports = {
  // Preset for TypeScript
  preset: 'ts-jest',
  transform: {
    '^.+\.(ts|tsx)$': ['ts-jest', {
      tsconfig: '<rootDir>/tsconfig.json',
    }],
  },
  
  // Test environment
  testEnvironment: 'jest-environment-jsdom',
  
  // Setup files - setup.js runs BEFORE imports
  setupFiles: ['<rootDir>/setup.js'],
  setupFilesAfterEnv: ['<rootDir>/setupTests.ts'],
  
  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  
  // Module name mapper for CSS and image files
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  
  // Transform configuration
  transform: {
    '^.+\.(ts|tsx)$': 'ts-jest',
  },
  
  // Test match pattern
  testMatch: ['**/?(*.)+(spec|test).+(ts|tsx|js)'],
  
  // Transform ignore patterns
  transformIgnorePatterns: [
    'node_modules/(?!(msw|@mswjs|@bundled-es-modules|until-async)/)',
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
    '!src/**/types.ts',
  ],
  
  coverageDirectory: '<rootDir>/coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  
  // Verbose output
  verbose: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Reset modules between tests
  resetModules: true,
  
  // Restore mocks between tests
  restoreMocks: true,

  // Global settings
  globals: {
    'ts-jest': {
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        skipLibCheck: true,
        noUnusedLocals: false,
        noUnusedParameters: false,
      },
      diagnostics: {
        ignoreCodes: ['TS2307', 'TS6133'],
      },
    },
  },
};