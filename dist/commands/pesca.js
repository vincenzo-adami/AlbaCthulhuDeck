import { SlashCommandBuilder } from "discord.js";
import { state } from "../state";
import { createDeck, shuffle } from "../utils/deck";
export const data = new SlashCommandBuilder()
    .setName("pesca")
    .setDescription("Pesca una carta per un giocatore (solo GM)")
    .addUserOption(option => option.setName("giocatore").setDescription("Il giocatore").setRequired(true));
export async function execute(interaction) {
    if (interaction.user.id !== state.gmId) {
        await interaction.reply("❌ Solo il GM può far pescare le carte.");
        return;
    }
    const player = interaction.options.getUser("giocatore", true);
    // se il giocatore non ha mazzo → crea
    if (!state.decks.has(player.id)) {
        state.decks.set(player.id, createDeck());
        state.piles.set(player.id, []);
    }
    let deck = state.decks.get(player.id);
    let pile = state.piles.get(player.id);
    // se mazzo finito → ricrea
    if (deck.length === 0) {
        deck = createDeck();
        state.decks.set(player.id, deck);
        pile = [];
        state.piles.set(player.id, pile);
    }
    const card = deck.shift();
    pile.push(card);
    let msg = `${player.username} ha pescato: **${card}**`;
    if (card === "A♠") {
        deck.push(...pile);
        shuffle(deck);
        state.decks.set(player.id, deck);
        state.piles.set(player.id, []);
        msg += "\n💥 È uscito l'Asso di Picche! Pila rimescolata nel mazzo.";
    }
    msg += `\n📦 Carte nel mazzo: ${deck.length}`;
    msg += `\n🃏 Carte nella pila: ${pile.length}`;
    await interaction.reply(msg);
}
