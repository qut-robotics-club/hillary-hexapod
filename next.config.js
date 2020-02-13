const withCSS = require("@zeit/next-css");
const withOffline = require("next-offline");
const { ProvidePlugin } = require('webpack');

module.exports = withCSS(withOffline({
    webpack: config => {
        config.plugins.push(new ProvidePlugin({
            THREE: ['three', 'THREE']
        }))

        return config;
    }
}));
