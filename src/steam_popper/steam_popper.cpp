#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "../sdk/public/steam/steam_api.h"

int main(int argc, char* argv[]) {

    if (argc < 3) {
        std::cerr << "Erro: Uso incorreto!" << std::endl;
        std::cerr << "Exemplo: .\\steam_popper.exe <AppID> <ID_da_Conquista_1> <ID_da_Conquista_2> ..." << std::endl;
        return 1;
    }

    std::ofstream appid_file("steam_appid.txt");
    appid_file << argv[1];
    appid_file.close();

    if (!SteamAPI_Init()) {
        std::cerr << "Erro Fatal: SteamAPI_Init() falhou. Verifique se o cliente Steam esta aberto." << std::endl;
        return 1;
    }


    for (int i = 2; i < argc; ++i) {
        const char* achievementID = argv[i];

        if (SteamUserStats()->SetAchievement(achievementID)) {
            std::cout << "Sucesso: Conquista '" << achievementID << "' marcada para desbloqueio." << std::endl;
        } else {
            std::cerr << "Aviso: Falha ao marcar a conquista '" << achievementID << "'. Verifique o ID." << std::endl;
        }
    }

    if (SteamUserStats()->StoreStats()) {
        std::cout << "Sucesso Final: As mudancas foram enviadas para os servidores da Steam!" << std::endl;
    } else {
        std::cerr << "Erro Fatal: StoreStats() falhou. Nao foi possivel salvar as conquistas." << std::endl;
    }


    SteamAPI_Shutdown();
    return 0; 
}