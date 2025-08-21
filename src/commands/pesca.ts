import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { state } from "../state.js";
import { createDeck, shuffle } from "../utils/deck.js";

export const data = new SlashCommandBuilder()
  .setName("pesca")
  .setDescription("Il GM fa pescare una carta a un giocatore")
  .addUserOption(option => option.setName("giocatore").setDescription("Seleziona il giocatore").setRequired(true));

export async function execute(interaction: ChatInputCommandInteraction) {
  if (interaction.user.id !== state.gm) {
    return interaction.reply({ content: "❌ Solo il GM può far pescare!", ephemeral: true });
  }

  const user = interaction.options.getUser("giocatore", true);
  let deck = state.decks.get(user.id);

  if (!deck) {
    deck = createDeck();
    state.decks.set(user.id, deck);
    state.discards.set(user.id, []);
  }

  const card = deck.shift()!;
  const discardPile = state.discards.get(user.id)!;
  discardPile.push(card);

  if (card === "A♠") {
    deck.push(...discardPile);
    shuffle(deck);
    state.discards.set(user.id, []);
  }

  await interaction.reply({ content: `🎴 ${user.username} ha pescato: ${card}`, ephemeral: false });
}
