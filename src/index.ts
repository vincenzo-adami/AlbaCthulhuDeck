import { Client, Collection, GatewayIntentBits, REST, Routes } from "discord.js";
import * as dotenv from "dotenv";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

// Fix __dirname in ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const commands = new Collection<string, any>();

// Caricamento comandi dinamico
const commandsPath = path.join(__dirname, "commands");
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith(".ts") || file.endsWith(".js"));

const restCommands: any[] = [];

for (const file of commandFiles) {
  const commandModule = await import(path.join(commandsPath, file));
  const command = commandModule;
  if (!command.data || !command.execute) continue;

  commands.set(command.data.name, command);
  restCommands.push(command.data.toJSON());
}

// Evento: bot pronto
client.once("ready", async () => {
  console.log(`✅ Loggato come ${client.user?.tag}`);

  // Registra i comandi nell’API di Discord
  const rest = new REST({ version: "10" }).setToken(process.env.TOKEN!);
  try {
    await rest.put(Routes.applicationCommands(client.user!.id), { body: restCommands });
    console.log("📦 Comandi registrati!");
  } catch (error) {
    console.error(error);
  }
});

// Evento: interazione comandi
client.on("interactionCreate", async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = commands.get(interaction.commandName);
  if (!command) return;

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({ content: "❌ Errore eseguendo il comando.", ephemeral: true });
    } else {
      await interaction.reply({ content: "❌ Errore eseguendo il comando.", ephemeral: true });
    }
  }
});

client.login(process.env.TOKEN);
