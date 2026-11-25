// node seednums.mjs <private seeds.json>   writes in/seednums.json: each seed id with only the numbers it contains, so the scheduler can check a post without seeing the seed
import fs from "fs"; import { numbers } from "./gate.mjs";
const s = JSON.parse(fs.readFileSync(process.argv[2], "utf8")); fs.writeFileSync("in/seednums.json", JSON.stringify(Object.fromEntries(Object.entries(s).map(([k, v]) => [k, numbers(v)])))); console.log(Object.keys(s).length, "seeds");
