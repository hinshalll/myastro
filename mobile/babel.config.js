module.exports = function (api) {
  api.cache(true);
  // babel-preset-expo (SDK 54) automatically adds the react-native-worklets
  // plugin that Reanimated v4 needs — do NOT add the old v3
  // 'react-native-reanimated/plugin' here.
  return {
    presets: ['babel-preset-expo'],
  };
};
