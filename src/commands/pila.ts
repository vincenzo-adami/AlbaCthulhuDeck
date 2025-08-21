import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { state } from "../state.js";

export const data = new SlashCommandBuilder()
  .setName("pila")
  .setDescription("Mostra la pila degli scarti di un giocatore (GM)");

export async function execute(interaction: ChatInputCommandInteraction) {
  if (interaction.user.id !== state.gm) {
    return interaction.reply({ content: "❌ Solo il GM può controllare la pila!", ephemeral: true });
  }

  const piles: string[] = [];
  for (const [userId, pile] of state.discards.entries()) {
    const username = interaction.guild?.members.cache.get(userId)?.user.username || "Unknown";
    piles.push(`${username}: ${pile.join(", ") || "vuota"}`);
  }

  await interaction.reply({ content: `📜 Pile degli scarti:\n${piles.join("\n")}`, ephemeral: true });
}
