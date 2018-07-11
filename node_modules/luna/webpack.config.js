module.exports = {
    entry: [ __dirname + '/src/index.ts' ],
    devtool: 'source-map',
    output: {
        path: __dirname,
        filename: 'bundle.js'
    },
    module: {
        loaders: [
            {
                test: /\.ts?$/,
                loader: 'awesome-typescript-loader',
                exclude: [ /node_modules/ ]
            }
        ]
    },
    resolve: {
        extensions: ['', '.ts', '.webpack.js', '.web.js', '.js', 'html'],
        modulesDirectories: ['node_modules']
    },
    exclude: [
        "example"
    ]

};