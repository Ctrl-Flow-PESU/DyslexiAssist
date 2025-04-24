const app = {
  init: function() {
    console.log('Application initialized');
  },
  
  config: {
    env: 'development',
    port: 3000
  },

  start: function() {
    this.init();
    console.log(`Server running on port ${this.config.port}`);
  }
};

app.start();