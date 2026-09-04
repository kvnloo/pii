// @ts-nocheck — loads under omp plugin runtime with ExtensionAPI injected
/**
 * omp-paw-pii — local PII redaction extension for Oh My Pi.
 *
 * Install:
 *   omp plugin link /path/to/pii/integrations/omp
 *
 * Requires a Python env where `python -m paw_pii.cli` works.
 * Complements built-in secrets.enabled (credentials) with NER-style PII.
 */
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

type SettingsKey =
	| "enabled"
	| "autoContext"
	| "autoProvider"
	| "autoToolResult"
	| "placeholder"
	| "pythonPath"
	| "module";

function readSetting(pi: ExtensionAPI, key: SettingsKey, fallback: unknown): unknown {
	try {
		if (typeof pi.getFlag === "function") {
			const flagged = pi.getFlag(key);
			if (flagged !== undefined) return flagged;
		}
		if (pi.pluginSettings && typeof pi.pluginSettings === "object" && key in pi.pluginSettings) {
			const value = pi.pluginSettings[key];
			if (value !== undefined) return value;
		}
	} catch {
		// settings surface differs across omp versions
	}
	return fallback;
}

async function runPythonRedact(
	pi: ExtensionAPI,
	mode: "redact" | "detect" | "redact-messages",
	payload: string,
	placeholder: string,
): Promise<string> {
	const pythonPath = String(readSetting(pi, "pythonPath", process.env.PAW_PII_PYTHON || "python3"));
	const moduleName = String(readSetting(pi, "module", "paw_pii.cli"));

	if (mode === "redact-messages") {
		const result = await pi.exec(pythonPath, ["-m", moduleName, "redact-messages", "--placeholder", placeholder], {
			stdin: payload,
		});
		if (result.code !== 0) {
			throw new Error(result.stderr || result.stdout || "paw-pii redact-messages failed");
		}
		return result.stdout;
	}

	const result = await pi.exec(
		pythonPath,
		["-m", moduleName, mode, "--placeholder", placeholder, "--text", payload],
		{},
	);
	if (result.code !== 0) {
		throw new Error(result.stderr || result.stdout || `paw-pii ${mode} failed`);
	}
	return result.stdout;
}

function collectTextParts(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	const chunks: string[] = [];
	for (const part of content) {
		if (!part || typeof part !== "object") continue;
		if (!("type" in part) || !("text" in part)) continue;
		if (part.type === "text" && typeof part.text === "string") chunks.push(part.text);
	}
	return chunks.join("\n");
}

function mapTextParts(content: unknown, redactedBlob: string): unknown {
	if (typeof content === "string") return redactedBlob;
	if (!Array.isArray(content)) return content;
	const textIndexes: number[] = [];
	for (let i = 0; i < content.length; i++) {
		const part = content[i];
		if (part && typeof part === "object" && "type" in part && part.type === "text") {
			textIndexes.push(i);
		}
	}
	if (textIndexes.length === 1) {
		const copy = content.slice();
		const idx = textIndexes[0];
		const prev = copy[idx];
		copy[idx] = typeof prev === "object" && prev ? { ...prev, text: redactedBlob } : { type: "text", text: redactedBlob };
		return copy;
	}
	if (textIndexes.length > 1) {
		return [{ type: "text", text: redactedBlob }];
	}
	return content;
}

export default function pawPiiExtension(pi: ExtensionAPI) {
	pi.setLabel("PAW PII Redaction");

	const isEnabled = () => readSetting(pi, "enabled", true) !== false;
	const placeholder = () =>
		String(readSetting(pi, "placeholder", process.env.PAW_PII_PLACEHOLDER || "[PII]"));

	pi.on("session_start", async (_event, ctx) => {
		if (!isEnabled()) return;
		ctx.ui?.notify?.("PAW PII redaction active (local)", "info");
	});

	pi.on("tool_result", async (event) => {
		if (!isEnabled() || readSetting(pi, "autoToolResult", true) === false || event.isError) return;
		try {
			const blob = collectTextParts(event.content);
			if (!blob || blob.length < 3) return;
			const redacted = (await runPythonRedact(pi, "redact", blob, placeholder())).replace(/\n$/, "");
			if (redacted === blob) return;
			return { content: mapTextParts(event.content, redacted) };
		} catch (err) {
			pi.logger?.warn?.("paw-pii tool_result redaction failed", { err: String(err) });
		}
	});

	pi.on("context", async (event) => {
		if (!isEnabled() || readSetting(pi, "autoContext", true) === false) return;
		try {
			const messages = event.messages;
			if (!Array.isArray(messages) || messages.length === 0) return;
			const out = await runPythonRedact(pi, "redact-messages", JSON.stringify(messages), placeholder());
			const parsed: unknown = JSON.parse(out);
			if (!Array.isArray(parsed)) return;
			return { messages: parsed };
		} catch (err) {
			pi.logger?.warn?.("paw-pii context redaction failed", { err: String(err) });
		}
	});

	pi.on("before_provider_request", async (event) => {
		if (!isEnabled() || readSetting(pi, "autoProvider", true) === false) return;
		try {
			const payload = event.payload;
			if (payload == null) return;
			if (typeof payload === "string") {
				return (await runPythonRedact(pi, "redact", payload, placeholder())).replace(/\n$/, "");
			}
			if (payload && typeof payload === "object" && !Array.isArray(payload) && "messages" in payload) {
				const messages = payload.messages;
				if (Array.isArray(messages)) {
					const msgs = await runPythonRedact(pi, "redact-messages", JSON.stringify(messages), placeholder());
					return { ...payload, messages: JSON.parse(msgs) };
				}
			}
			const raw = JSON.stringify(payload);
			const envelope = await runPythonRedact(
				pi,
				"redact-messages",
				JSON.stringify([{ content: raw }]),
				placeholder(),
			);
			const parsed: unknown = JSON.parse(envelope);
			if (!Array.isArray(parsed) || !parsed[0] || typeof parsed[0] !== "object") return;
			const first = parsed[0];
			if (!("content" in first)) return;
			const redactedRaw = first.content;
			if (typeof redactedRaw === "string" && redactedRaw !== raw) {
				try {
					return JSON.parse(redactedRaw);
				} catch {
					return payload;
				}
			}
		} catch (err) {
			pi.logger?.warn?.("paw-pii before_provider_request failed", { err: String(err) });
		}
	});

	const z = pi.zod;
	pi.registerTool({
		name: "detect_pii",
		label: "Detect PII",
		description: "Detect PII locally with ProgramAsWeights. Returns typed spans JSON.",
		parameters: z.object({
			text: z.string().describe("Text to scan"),
		}),
		async execute(_id, params) {
			const out = await runPythonRedact(pi, "detect", params.text, placeholder());
			return { content: [{ type: "text", text: out }] };
		},
	});

	pi.registerTool({
		name: "redact_pii",
		label: "Redact PII",
		description: "Redact PII from text locally and return the scrubbed string.",
		parameters: z.object({
			text: z.string().describe("Text to redact"),
		}),
		async execute(_id, params) {
			const out = (await runPythonRedact(pi, "redact", params.text, placeholder())).replace(/\n$/, "");
			return { content: [{ type: "text", text: out }] };
		},
	});

	pi.registerCommand("pii-status", {
		description: "Show PAW PII plugin status",
		handler: async (_args, ctx) => {
			ctx.ui?.notify?.(
				`paw-pii enabled=${isEnabled()} placeholder=${placeholder()} python=${readSetting(pi, "pythonPath", "python3")}`,
				"info",
			);
		},
	});
}
