module.exports = {
  apps: [
    {
      name: "API Hub",
      script: "/root/.pyenv/versions/apihub/bin/uvicorn",
      args: "main:app --port 9999 --no-access-log",
      interpreter: "/root/.pyenv/versions/apihub/bin/python",
      env: {
        ENV: "prod",
      },
    },
    {
      name: "Scheduler",
      script: "scheduler.py",
      interpreter: "/root/.pyenv/versions/apihub/bin/python",
      env: {
        ENV: "prod",
      },
    },
  ],
};
