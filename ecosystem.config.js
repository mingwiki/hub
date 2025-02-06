module.exports = {
  apps: [
    {
      name: "API Hub",
      script: "/root/.pyenv/versions/apihub/bin/uvicorn",
      args: "main:app --port 9999 --no-access-log --loop uvloop",
      cwd: "/root/apihub",
      interpreter: "/root/.pyenv/versions/apihub/bin/python",
      env: {
        ENV: "prod",
      },
    },
    {
      name: "Scheduler",
      script: "/root/.pyenv/versions/apihub/bin/python",
      args: "scheduler.py",
      cwd: "/root/apihub",
      env: {
        ENV: "prod",
      },
    },
  ],
};
