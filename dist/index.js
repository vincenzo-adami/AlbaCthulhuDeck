import { Client, Collection, GatewayIntentBits, REST, Routes } from "discord.js";
import * as dotenv from "dotenv";
import fs from "fs";
import path from "path";
dotenv.config();
const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const commands = new Collection();
// Caricamento comandi dinamico
const commandsPath = path.join(__dirname, "commands");
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith(".ts") || file.endsWith(".js"));
const restCommands = [];
for (const file of commandFiles) {
    const command = require(path.join(commandsPath, file));
    commands.set(command.data.name, command);
    restCommands.push(command.data.toJSON());
}
client.once("ready", async () => {
    console.log(`✅ Loggato come ${client.user?.tag}`);
    // Registra i comandi nell'API di Discord
    const rest = new REST({ version: "10" }).setToken(process.env.TOKEN);
    await rest.put(Routes.applicationCommands(client.user.id), { body: restCommands });
    console.log("📦 Comandi registrati!");
});
client.on("interactionCreate", async (interaction) => {
    if (!interaction.isChatInputCommand())
        return;
    const command = commands.get(interaction.commandName);
    if (!command)
        return;
    try {
        await command.execute(interaction);
    }
    catch (error) {
        console.error(error);
        await interaction.reply({ content: "❌ Errore eseguendo il comando.", ephemeral: true });
    }
});
client.login(process.env.TOKEN);
