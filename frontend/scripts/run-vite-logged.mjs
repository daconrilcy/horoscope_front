// Centralise les sorties Vite et Vitest dans un dossier de logs dedie au frontend.
import { createWriteStream, mkdirSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { spawn } from "node:child_process"

const scriptDirectory = dirname(fileURLToPath(import.meta.url))
const frontendRoot = resolve(scriptDirectory, "..")
const [tool, logName, ...toolArgs] = process.argv.slice(2)

if (!["vite", "vitest"].includes(tool) || !/^[a-zA-Z0-9._-]+$/.test(logName ?? "")) {
  console.error("Usage: node scripts/run-vite-logged.mjs <vite|vitest> <log-name> [...args]")
  process.exit(1)
}

const logDirectory = join(frontendRoot, "logs", "vite")
mkdirSync(logDirectory, { recursive: true })

const stdoutLog = createWriteStream(join(logDirectory, `${logName}.log`), { flags: "w" })
const stderrLog = createWriteStream(join(logDirectory, `${logName}.err.log`), { flags: "w" })
const executable = join(frontendRoot, "node_modules", ".bin", `${tool}.cmd`)

// Relaye les flux vers le terminal tout en conservant une copie fichier unique.
const child = spawn(executable, toolArgs, {
  cwd: frontendRoot,
  shell: true,
  stdio: ["inherit", "pipe", "pipe"],
})

child.stdout.on("data", (chunk) => {
  process.stdout.write(chunk)
  stdoutLog.write(chunk)
})

child.stderr.on("data", (chunk) => {
  process.stderr.write(chunk)
  stderrLog.write(chunk)
})

child.on("error", (error) => {
  stderrLog.write(`${error.message}\n`)
  console.error(error.message)
  process.exitCode = 1
})

child.on("close", (code) => {
  stdoutLog.end()
  stderrLog.end()
  process.exit(code ?? 1)
})
