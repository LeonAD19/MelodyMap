// jest.config.js
module.exports = {
  testEnvironment: "node",
  reporters: [
    "default",
    ["jest-html-reporter", {
      pageTitle: "Melody Map Test Report",
      outputPath: "jest-report.html",
      includeFailureMsg: true,
      includeSuiteFailure: true
    }]
  ],
  testMatch: ["**/flask_folder/tests/**/*.test.cjs"] // adjust path if needed
};
