module.exports = {
  apps : [{
    name: 'echo-python-3',
    cmd: 'main.py',
    interpreter: 'python3',
    //args: 'arg1 arg2',
    autorestart: false,
    watch: true,
    //pid: '/path/to/pid/file.pid',
    //instances: 4,
    max_memory_restart: '3G',
    env: {
      ENV: 'development'
    },
    env_production : {
      ENV: 'production'
    }
  }]
};
