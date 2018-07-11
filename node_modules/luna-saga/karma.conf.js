// Karma configuration
// Generated on Sun Dec 06 2015 01:12:24 GMT-0600 (CST)
var webpackConfig = require('./webpack.config');
webpackConfig.devtool = 'inline-source-map';
webpackConfig.stats = { colors: true, reasons: true };

module.exports = function (config) {
    config.set({
        basePath: '',
        frameworks: ['jasmine'],
        files: [
            "src/index.spec.ts"
            //'src/*.spec.ts'
        ],
        exclude: [],
        preprocessors: {
            "**/*.ts": ["webpack", "sourcemap"]
        },
        // note: necessary for karma script to execute properly in Chrome.
        // Otherwise mime type is recognized as video, result in an error message.
        mime: {
            'text/x-typescript': ['ts','tsx']
        },
        webpack: webpackConfig,
        webpackMiddleware: { noInfo: true },
        reporters: ['progress'],
        port: 9876,
        colors: true,
        // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
        logLevel: config.LOG_INFO,
        autoWatch: true,
        browsers: ['Chrome'],
        // ad this timeout manually to prevent browser disconnect
        browserNoActivityTimeout: 100000,
        singleRun: false,
        // Concurrency level
        // how many browser should be started simultaneously
        concurrency: Infinity
    });
};
