import { SlashCommandBuilder } from "discord.js";
import { state } from "../state";
export const data = new SlashCommandBuilder()
    .setName("pila")
    .setDescription("Mostra la tua pila di carte pescate");
export async function execute(interaction) {
    const pile = state.piles.get(interaction.user.id) ?? [];
    if (pile.length === 0) {
        await interaction.reply("Non hai ancora pescato nessuna carta.");
        return;
    }
    const last = pile[pile.length - 1];
    await interaction.reply(`La tua pila: ${pile.join(", ")}\n🔹 Ultima: **${last}**`);
}
