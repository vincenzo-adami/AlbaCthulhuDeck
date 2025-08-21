import { SlashCommandBuilder } from "discord.js";
import { state } from "../state.js";
export const data = new SlashCommandBuilder()
    .setName("carte")
    .setDescription("Mostra la pila degli scarti del tuo mazzo");
export async function execute(interaction) {
    const userId = interaction.user.id;
    const deck = state.decks.get(userId);
    if (!deck) {
        return interaction.reply({ content: "❌ Non hai ancora un mazzo.", ephemeral: true });
    }
    const pile = state.discards.get(userId) || [];
    await interaction.reply({ content: `📜 Pila degli scarti: ${pile.join(", ") || "vuota"}`, ephemeral: true });
}
