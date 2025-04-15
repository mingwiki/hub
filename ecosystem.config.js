module.exports = {
  apps: [
    {
      name: "API Hub",
      script: "/root/.pyenv/versions/apihub/bin/uvicorn",
      args: "src.main:app --port 9999 --no-access-log",
      interpreter: "/root/.pyenv/versions/apihub/bin/python",
      env: {
        ENV: "prod",
      },
    },
    {
      name: "Scheduler",
      script: "/root/.pyenv/versions/apihub/bin/python -m src.scheduler",
      cwd: "./",
      env: {
        ENV: "prod",
      },
    },
  ],
};
