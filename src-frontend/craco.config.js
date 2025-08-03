const Critters = require('critters-webpack-plugin');

module.exports = {
    webpack: {
        plugins: {
            add: [
                new Critters({
                    // Critters options
                    preload: 'swap', // or 'body'
                    preloadFonts: true,
                    fonts: true,
                    noscriptFallback: true
                })
            ]
        }
    }
};