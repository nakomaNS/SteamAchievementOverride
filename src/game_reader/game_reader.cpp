#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <windows.h> 
#include "json.hpp"
#include "steam/steam_api.h"


std::string RemoveSpecialCharacters(const std::string& input) {
    std::string result;
    for (char c : input) {
        if (std::isalnum(c) || c == ' ' || c == '-' || c == '_') {
            result += c;
        }
    }
    while (result.find("  ") != std::string::npos) {
        result.replace(result.find("  "), 2, " ");
    }
    result.erase(0, result.find_first_not_of(' '));
    result.erase(result.find_last_not_of(' ') + 1);
    return result;
}

std::map<unsigned int, std::string> LoadDatabaseFromFile();

struct GameInfo {
    AppId_t id;
    std::string name;
    bool operator<(const GameInfo& other) const {
        return id < other.id;
    }
};

int main(int argc, char* argv[]) {
    SetConsoleOutputCP(CP_UTF8);

    std::ofstream appid_file("steam_appid.txt");
    appid_file << "480";
    appid_file.close();

    bool steam_api_initialized = SteamAPI_Init();
    if (!steam_api_initialized) {
        std::cerr << "Aviso: Falha ao inicializar SteamAPI. Listando todos os jogos do applist.json." << std::endl;
    }

    std::map<unsigned int, std::string> allGames = LoadDatabaseFromFile();
    if (allGames.empty()) {
        if (SteamAPI_IsSteamRunning()) {
            SteamAPI_Shutdown();
            std::cerr << "Erro: Banco de dados vazio e Steam está rodando." << std::endl;
            return 1;
        }
        std::cerr << "Aviso: Banco de dados vazio, mas Steam não está rodando. Continuando..." << std::endl;
    }

    const std::vector<std::string> palavras_proibidas = {
        "server", "sdk", "demo", "beta", "dlc", "editor", "toolkit",
        "authoring tools", "benchmark", "dedicated", "bonus content",
        "configs", "redist", "test", "pack", "kit", "steam", "valve",
        "linux", "vr", "controller", "sharing", "client", "awards",
        "filmmaker", "add-on", "winui2", "slice", "greenlight",
        "depot", "key", "rgl/sc"
    };

    std::vector<GameInfo> jogos_filtrados_passo1;
    for (const auto& pair : allGames) {
        bool include_game = false;
        if (steam_api_initialized) {
            if (SteamApps()->BIsSubscribedApp(pair.first)) {
                include_game = true;
            }
        } else {
            include_game = true;
        }

        if (include_game) {
            bool ignorar = false;
            std::string gameNameLower = pair.second;
            std::transform(gameNameLower.begin(), gameNameLower.end(), gameNameLower.begin(),
                           [](unsigned char c) { return std::tolower(c); });

            for (const auto& palavra : palavras_proibidas) {
                if (gameNameLower.find(palavra) != std::string::npos) {
                    ignorar = true;
                    break;
                }
            }
            if (!ignorar) {
                jogos_filtrados_passo1.push_back({pair.first, pair.second});
            }
        }
    }

    std::sort(jogos_filtrados_passo1.begin(), jogos_filtrados_passo1.end());

    const std::vector<std::string> whitelist_keywords = {"episode", "deathmatch", "source"};
    std::vector<GameInfo> lista_final;

    for (const auto& jogo_atual : jogos_filtrados_passo1) {
        bool is_dlc_de_conteudo = false;
        for (const auto& jogo_base : jogos_filtrados_passo1) {
            if (jogo_atual.id == jogo_base.id) continue;

            if (jogo_atual.name.rfind(jogo_base.name, 0) == 0 && jogo_atual.name.length() > jogo_base.name.length()) {
                std::string parte_extra = jogo_atual.name.substr(jogo_base.name.length());
                std::transform(parte_extra.begin(), parte_extra.end(), parte_extra.begin(),
                               [](unsigned char c) { return std::tolower(c); });

                bool esta_na_whitelist = false;
                for (const auto& keyword : whitelist_keywords) {
                    if (parte_extra.find(keyword) != std::string::npos) {
                        esta_na_whitelist = true;
                        break;
                    }
                }
                if (!esta_na_whitelist) {
                    is_dlc_de_conteudo = true;
                    break;
                }
            }
        }
        if (!is_dlc_de_conteudo) {
            lista_final.push_back(jogo_atual);
        }
    }

    for (const auto& jogo : lista_final) {
        std::string clean_name = RemoveSpecialCharacters(jogo.name);
        std::cout << clean_name << " (AppID: " << jogo.id << ")" << std::endl;
    }

    if (steam_api_initialized) {
        SteamAPI_Shutdown();
    }
    return 0;
}

std::map<unsigned int, std::string> LoadDatabaseFromFile() {
    const std::string filename = "applist.json";
    std::map<unsigned int, std::string> gameDatabase;

    std::cout << "Carregando banco de dados de jogos do arquivo local '" << filename << "'..." << std::endl;

    std::ifstream db_file(filename, std::ios::binary);
    if (!db_file.is_open()) {
        std::cerr << "ERRO CRITICO: Nao foi possivel encontrar o arquivo '" << filename << "'!" << std::endl;
        std::cerr << "Certifique-se de que ele esta no caminho correto." << std::endl;
        return gameDatabase;
    }

    nlohmann::json j;
    try {
        db_file >> j;
    } catch (nlohmann::json::parse_error& e) {
        std::cerr << "ERRO CRITICO: Falha ao analisar o arquivo JSON: " << e.what() << std::endl;
        return gameDatabase;
    }

    for (const auto& app : j["applist"]["apps"]) {
        if (!app["name"].get<std::string>().empty()) {
            std::string name = app["name"].get<std::string>();
            gameDatabase[app["appid"].get<unsigned int>()] = name;
        }
    }

    std::cout << "Banco de dados com " << gameDatabase.size() << " jogos carregado com sucesso." << std::endl;

    return gameDatabase;
}