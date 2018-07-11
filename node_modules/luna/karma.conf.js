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
            'src/index.spec.ts' // just use index to import everything
            //'src/*.spec.ts'
        ],
        // note: necessary for karma script to execute properly in Chrome.
        // Otherwise mime type is recognized as video, result in an error message.
        mime: {
            'text/x-typescript': ['ts','tsx']
        },
        exclude: [],
        preprocessors: {
            "**/*.spec.ts": ["webpack", "sourcemap"]
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
        singleRun: false,
        // Concurrency level
        // how many browser should be started simultanous
        concurrency: Infinity
    });
};
