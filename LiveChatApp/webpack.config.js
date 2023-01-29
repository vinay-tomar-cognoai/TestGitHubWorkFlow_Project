const path = require("path");
module.exports = {
  mode: 'development',
  entry: "./src/js/livechat.js",
  output: {
    path: path.resolve(__dirname, "static/LiveChatApp/js"),
    filename: "bundle.js"
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /(node_modules)/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env"]
          }
        }
      }
    ]
  }
};
