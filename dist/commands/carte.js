import { SlashCommandBuilder } from "discord.js";
import { state } from "../state";
export const data = new SlashCommandBuilder()
    .setName("carte")
    .setDescription("Mostra quante carte restano nel tuo mazzo");
export async function execute(interaction) {
    const deck = state.decks.get(interaction.user.id);
    if (!deck) {
        await interaction.reply("Non hai ancora un mazzo. Ti verrà creato alla prima pescata.");
        return;
    }
    await interaction.reply(`📦 Carte rimaste nel tuo mazzo: ${deck.length}`);
}
