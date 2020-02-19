const withCSS = require("@zeit/next-css");
const withOffline = require("next-offline");
const { ProvidePlugin } = require("webpack");

const { NODE_ENV } = process.env;

module.exports = withCSS(
  withOffline({
    env: {
      DEV_MODE: NODE_ENV === "development"
    },

    webpack: config => {
      config.plugins.push(
        new ProvidePlugin({
          THREE: ["three", "THREE"]
        })
      );

      return config;
    }
  })
);
