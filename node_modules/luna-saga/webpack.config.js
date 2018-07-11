var CheckerPlugin = require('awesome-typescript-loader').CheckerPlugin;
module.exports = {
    // entry: [__dirname + '/src/index.ts'],
    devtool: '#inline-source-map',
    output: {
        path: __dirname,
        filename: 'bundle.js'
    },
    resolve: {
        extensions: ['', '.ts', '.webpack.js', '.web.js', '.js', 'html'],
        modulesDirectories: ['node_modules']
    },
    exclude: [
        "example"
    ],
    module: {
        loaders: [
            {
                test: /\.ts?$/,
                loaders: ['awesome-typescript-loader'],
                exclude: [/node_modules/]
            }
        ]
    },
    plugins: [
        new CheckerPlugin()
    ]
};