// webpack.config.js
const webpack = require('webpack');

module.exports = {
    resolve: {
        fallback: {
            "path": require.resolve("path-browserify"),
            "assert": require.resolve("assert/"),
            "util": require.resolve("util/"),
            "stream": require.resolve("stream-browserify"),
            "process": require.resolve("process/browser"),
            "buffer": require.resolve("buffer/")
        }
    },
    plugins: [
        new webpack.ProvidePlugin({
            process: 'process/browser',
            Buffer: ['buffer', 'Buffer']
        })
    ]
};
