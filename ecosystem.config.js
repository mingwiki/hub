module.exports = {
  apps: [
    {
      name: "API Hub",
      script: "uvicorn",
      args: "main:app --port 9999 --no-access-log --loop uvloop",
      interpreter: ".venv/bin/python",
      env: {
        ENV: "prod",
      },
    },
    {
      name: "Scheduler",
      script: "scheduler.py",
      interpreter: ".venv/bin/python",
      env: {
        ENV: "prod",
      },
    },
  ],
};
