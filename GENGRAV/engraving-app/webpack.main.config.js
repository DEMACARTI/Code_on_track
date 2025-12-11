module.exports = {
  entry: './src/main.js',
  module: {
    rules: require('./webpack.rules'),
  },
  externals: {
    'serialport': 'commonjs serialport',
    '@serialport/parser-readline': 'commonjs @serialport/parser-readline',
    '@serialport/bindings-cpp': 'commonjs @serialport/bindings-cpp'
  }
};

