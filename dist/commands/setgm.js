import { SlashCommandBuilder } from "discord.js";
import { state } from "../state.js";
export const data = new SlashCommandBuilder()
    .setName("setgm")
    .setDescription("Imposta il GM del gioco")
    .addUserOption(option => option.setName("giocatore").setDescription("Seleziona il GM").setRequired(true));
export async function execute(interaction) {
    const user = interaction.options.getUser("giocatore", true);
    state.gm = user.id;
    await interaction.reply({ content: `✅ ${user.username} è ora il GM`, ephemeral: false });
}
