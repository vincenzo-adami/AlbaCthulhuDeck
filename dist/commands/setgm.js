import { SlashCommandBuilder } from "discord.js";
import { state } from "../state";
export const data = new SlashCommandBuilder()
    .setName("setgm")
    .setDescription("Imposta il Game Master")
    .addUserOption(option => option.setName("membro").setDescription("Il nuovo GM").setRequired(true));
export async function execute(interaction) {
    const member = interaction.options.getUser("membro", true);
    state.gmId = member.id;
    await interaction.reply(`👑 ${member.username} è ora il Game Master!`);
}
