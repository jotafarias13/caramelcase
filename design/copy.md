# caramelCase · interface copy

All interface text in Brazilian Portuguese (primary) and English, keyed by screen. Screen keys match the file names in `screens/` without the device suffix: `v1.session-1-selected` is `screens/v1-session-1-selected-mobile.html` and `-desktop.html`.

- **Voice:** a sharp classmate. Informal "você", everyday Brazilian phrasing, encouragement on wrong answers, never sarcasm.
- **Variables:** numbers, names, dates and times inside a string are sample values. Treat them as variables when wiring i18n, for example `Faltam {n} questões`.
- **Sample content:** question text, options, reasons, subject and topic names, people and scores come from the database in production. They are listed so the mockups can be reproduced exactly.
- **Placeholders:** text in [BRACKETS] is not decided yet: plan benefits, yearly prices, the referral reward, the exam name and the domain.
- **Accessibility text:** `aria-label` and image descriptions are included, since they need translating too.
- **Not listed:** the English session mockup (`v1-flow-english`), and the app-icon and safe-area boards, which are documentation rather than interface.

## common

Strings that appear on four or more screens. They are not repeated in the screen sections below.

| Key | PT-BR | EN |
| --- | --- | --- |
| `common.leave_session` | Sair da sessão | Leave session |
| `common.session_progress` | Progresso da sessão | Session progress |
| `common.programming` | Programação | Programming |
| `common.recursion` | Recursão | Recursion |
| `common.easy` | Fácil | Easy |
| `common.what_does_this_program_print` | O que este programa imprime? | What does this program print? |
| `common.options` | Alternativas | Options |
| `common.recursionerror` | RecursionError | RecursionError |
| `common.check` | Verificar | Check |
| `common.enter` | Enter | Enter |
| `common.10_would_be_the_sum_4_3_2_1_the_program` | 10 seria a soma 4 + 3 + 2 + 1. O programa multiplica. | 10 would be the sum 4 + 3 + 2 + 1. The program multiplies. |
| `common.f_4_4_3_2_1_24` | f(4) = 4 × 3 × 2 × 1 = 24. | f(4) = 4 × 3 × 2 × 1 = 24. |
| `common.16_would_be_4_4_each_call_multiplies_by` | 16 seria 4 × 4. Cada chamada multiplica por f(n - 1), não por n de novo. | 16 would be 4 × 4. Each call multiplies by f(n - 1), not by n again. |
| `common.the_base_case_n_1_ends_the_recursion_so` | O caso base n <= 1 encerra a recursão, então não há erro. | The base case n <= 1 ends the recursion, so there is no error. |
| `common.mel_celebrating` | Mel comemorando | Mel celebrating |
| `common.nailed_it` | Mandou bem! | Nailed it! |
| `common.report_question` | Reportar questão | Report question |
| `common.continue` | Continuar | Continue |
| `common.correct_answer` | Resposta certa | Correct answer |
| `common.your_answer` | Sua resposta | Your answer |
| `common.mel_encouraging` | Mel incentivando | Mel encouraging |
| `common.close_here_s_why` | Quase. Olha só o porquê: | Close. Here's why: |
| `common.close` | Fechar | Close |
| `common.session_complete` | Sessão concluída! | Session complete! |
| `common.out_of_10_correct` | de 10 certas | out of 10 correct |
| `common.xp` | xp | xp |
| `common.rating` | rating | rating |
| `common.streak` | sequência | streak |
| `common.7_days` | 7 dias | 7 days |
| `common.level_4` | Nível 4 | Level 4 |
| `common.level_xp` | XP do nível | Level XP |
| `common.topics_to_review` | Tópicos pra revisar | Topics to review |
| `common.1_miss` | 1 erro | 1 miss |
| `common.binary_search` | Busca binária | Binary search |
| `common.one_more` | Mais uma | One more |
| `common.back_to_home` | Voltar pro início | Back to home |
| `common.send` | Enviar | Send |
| `common.stacks_and_queues` | Pilhas e filas | Stacks and queues |
| `common.mel_waving` | Mel acenando | Mel waving |
| `common.operating_systems` | Sistemas Operacionais | Operating Systems |
| `common.medium` | Médio | Medium |
| `common.algorithms` | Algoritmos | Algorithms |
| `common.let_s_practice` | Bora praticar | Let's practice |
| `common.data_structures` | Estruturas de Dados | Data Structures |
| `common.which_data_structure_follows_the_lifo_la` | Qual estrutura de dados segue a política LIFO (último a entrar, primeiro a sair)? | Which data structure follows the LIFO (last in, first out) policy? |
| `common.ds` | ed/ | ds/ |
| `common.databases` | Bancos de Dados | Databases |
| `common.networks` | Redes | Networks |
| `common.step` | Etapa | Step |
| `common.skip` | Pular | Skip |
| `common.mel` | Mel | Mel |
| `common.back` | Voltar | Back |
| `common.hey_carol` | E aí, Carol! | Hey, Carol! |
| `common.switch_subject_current_data_structures` | Trocar matéria. Atual: Estruturas de Dados | Switch subject. Current: Data Structures |
| `common.today_s_goal_12_of_20_questions` | Meta de hoje: 12 de 20 questões | Today's goal: 12 of 20 questions |
| `common.today_s_goal` | meta de hoje | today's goal |
| `common.8_questions_to_go` | Faltam 8 questões | 8 questions to go |
| `common.next_linked_lists` | Próximo: Listas ligadas | Next: Linked lists |
| `common.topics` | Tópicos | Topics |
| `common.mastered` | Dominado | Mastered |
| `common.linked_lists` | Listas ligadas | Linked lists |
| `common.in_progress` | Em andamento | In progress |
| `common.binary_trees` | Árvores binárias | Binary trees |
| `common.start` | Começar | Start |
| `common.hash_tables` | Tabelas hash | Hash tables |
| `common.graphs` | Grafos | Graphs |
| `common.locked` | Bloqueado | Locked |
| `common.main` | Principal | Main |
| `common.home` | Início | Home |
| `common.profile` | Perfil | Profile |
| `common.settings` | Ajustes | Settings |
| `common.7_day_streak` | 7 dias seguidos | 7-day streak |
| `common.mel_sleeping` | Mel dormindo | Mel sleeping |
| `common.review` | Revisão | Review |
| `common.leagues` | Ligas | Leagues |
| `common.progress` | Progresso | Progress |
| `common.what_is_the_worst_case_time_complexity_o` | Qual é a complexidade de tempo, no pior caso, da busca binária em um vetor ordenado de n elementos? | What is the worst-case time complexity of binary search on a sorted array of n elements? |
| `common.o_1` | O(1) | O(1) |
| `common.o_log_n` | O(log n) | O(log n) |
| `common.o_n` | O(n) | O(n) |
| `common.o_n_log_n` | O(n log n) | O(n log n) |
| `common.questions` | Questões | Questions |
| `common.billing` | Cobrança | Billing |
| `common.monthly` | Mensal | Monthly |
| `common.yearly` | Anual | Yearly |
| `common.month` | /mês | /month |
| `common.recommended` | Recomendado | Recommended |
| `common.see_plans` | Ver planos | See plans |
| `common.pro` | pro | pro |

## V1

### v1.session-1-selected · Session · option selected

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.session-1-selected.select` | escolher | select |
| `v1.session-1-selected.check` | verificar | check |

### v1.session-3-correct · Feedback · correct

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.session-3-correct.correct` | Correta | Correct |

### v1.session-4-wrong · Feedback · wrong

Uses common strings only.

### v1.summary-gain · Summary · rating gain

Uses common strings only.

### v1.report · Report a question

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.report.what_s_wrong_with_it` | O que tem de errado nela? | What's wrong with it? |
| `v1.report.wrong_answer` | Resposta errada | Wrong answer |
| `v1.report.ambiguous_wording` | Enunciado ambíguo | Ambiguous wording |
| `v1.report.typo` | Erro de digitação | Typo |
| `v1.report.other` | Outro | Other |
| `v1.report.details_optional` | Detalhes (opcional) | Details (optional) |
| `v1.report.tell_us_what_you_saw` | Conta pra gente o que você viu. | Tell us what you saw. |
| `v1.report.cancel` | Cancelar | Cancel |

### v1.session-0-default · Session · nothing selected

Uses common strings only.

### v1.session-2-checking · Answer reveal · checking

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.session-2-checking.checking` | Verificando… | Checking… |

### v1.session-5-reasons-off · Feedback · reasons off

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.session-5-reasons-off.f_computes_the_factorial_f_4_4_3_2_1_24` | f calcula o fatorial. f(4) = 4 × 3 × 2 × 1 = 24. | f computes the factorial. f(4) = 4 × 3 × 2 × 1 = 24. |

### v1.summary-loss · Summary · rating loss

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.summary-loss.session_complete` | Sessão concluída | Session complete |
| `v1.summary-loss.tough_days_happen_the_questions_you_miss` | Dia difícil acontece. As questões que você errou voltam pra revisar. | Tough days happen. The questions you missed will come back for review. |
| `v1.summary-loss.your_rating_dipped_a_little_the_next_ses` | Seu rating desceu um pouco. A próxima sessão vem mais leve e ele volta rápido. | Your rating dipped a little. The next session will be lighter and it comes back fast. |
| `v1.summary-loss.2_misses` | 2 erros | 2 misses |

### v1.summary-save · Summary · save progress prompt

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.summary-save.want_to_save_this_progress` | Quer salvar esse progresso? | Want to save this progress? |
| `v1.summary-save.create_an_account_to_keep_your_streak_yo` | Crie uma conta e guarde sua sequência, seu rating e os tópicos pra revisar. | Create an account to keep your streak, your rating and your topics to review. |
| `v1.summary-save.save_my_progress` | Salvar meu progresso | Save my progress |
| `v1.summary-save.not_now` | Agora não | Not now |

### v1.flow-longtext-pt · Long text · Portuguese

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-longtext-pt.memory_management` | Gerenciamento de memória | Memory management |
| `v1.flow-longtext-pt.in_a_system_with_demand_paging_what_happ` | Em um sistema com paginação por demanda, o que acontece quando um processo acessa uma página que não está na memória principal? | In a system with demand paging, what happens when a process accesses a page that is not in main memory? |
| `v1.flow-longtext-pt.a_page_fault_occurs_and_the_operating_sy` | Ocorre uma falta de página e o sistema operacional carrega a página do disco | A page fault occurs and the operating system loads the page from disk |
| `v1.flow-longtext-pt.the_process_is_terminated_immediately_wi` | O processo é encerrado imediatamente com erro de segmentação | The process is terminated immediately with a segmentation fault |
| `v1.flow-longtext-pt.the_processor_ignores_the_access_and_mov` | O processador ignora o acesso e segue para a próxima instrução | The processor ignores the access and moves on to the next instruction |
| `v1.flow-longtext-pt.the_page_is_created_empty_in_memory_with` | A página é criada vazia na memória, sem consultar o disco | The page is created empty in memory, without checking the disk |
| `v1.flow-longtext-pt.select` | escolher | select |
| `v1.flow-longtext-pt.check` | verificar | check |

### v1.flow-code · Code on a small screen

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-code.what_does_this_function_return_for_vetor` | O que esta função devolve para vetor = [1, 3, 5, 7, 9] e alvo = 7? | What does this function return for vetor = [1, 3, 5, 7, 9] and alvo = 7? |

### v1.flow-offline-1 · Offline · interrupted mid-question

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-offline-1.you_re_offline_your_answers_are_saved_on` | Você está offline. Suas respostas ficam salvas neste aparelho. | You're offline. Your answers are saved on this device. |

### v1.flow-offline-2 · Offline · resumed

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-offline-2.back_online_session_synced` | De volta online. Sessão sincronizada. | Back online. Session synced. |

### v1.landing · Landing page

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.landing.language_english` | Idioma: Português (Brasil) | Language: English |
| `v1.landing.en` | PT-BR | EN |
| `v1.landing.sign_in` | Entrar | Sign in |
| `v1.landing.ready_to_practice` | Bora praticar? | Ready to practice? |
| `v1.landing.computer_science_in_five_minute_sessions` | Ciência da computação em sessões de cinco minutos. | Computer science in five-minute sessions. |
| `v1.landing.pick_a_subject_answer_a_short_run_of_que` | Escolha uma matéria, responda uma sequência curta de questões e entenda cada resposta. | Pick a subject, answer a short run of questions and understand every answer. |
| `v1.landing.no_sign_up_just_start` | sem cadastro · é só começar | no sign-up · just start |
| `v1.landing.try_it_answer_without_an_account` | // experimente: responda sem criar conta | // try it: answer without an account |
| `v1.landing.queue` | Fila | Queue |
| `v1.landing.stack` | Pilha | Stack |
| `v1.landing.linked_list` | Lista ligada | Linked list |
| `v1.landing.binary_tree` | Árvore binária | Binary tree |
| `v1.landing.five_subjects_to_start_with` | Cinco matérias pra começar | Five subjects to start with |
| `v1.landing.alg` | alg/ | alg/ |
| `v1.landing.os` | so/ | os/ |
| `v1.landing.db` | bd/ | db/ |
| `v1.landing.net` | redes/ | net/ |
| `v1.landing.how_it_works` | Como funciona | How it works |
| `v1.landing.five_minutes` | Cinco minutos | Five minutes |
| `v1.landing.8_to_12_questions_per_session_it_fits_on` | De 8 a 12 questões por sessão. Dá pra fazer no ônibus ou entre duas aulas. | 8 to 12 questions per session. It fits on the bus or between two classes. |
| `v1.landing.difficulty_that_keeps_up_with_you` | Dificuldade que te acompanha | Difficulty that keeps up with you |
| `v1.landing.you_have_a_rating_like_in_chess_get_it_r` | Você tem um rating, como no xadrez. Acertou, ele sobe e vêm questões mais difíceis. | You have a rating, like in chess. Get it right and it goes up, and harder questions follow. |
| `v1.landing.the_why_behind_every_answer` | O porquê de cada resposta | The why behind every answer |
| `v1.landing.after_you_answer_you_see_why_each_option` | Depois de responder, você vê por que cada alternativa está certa ou errada. | After you answer, you see why each option is right or wrong. |
| `v1.landing.five_minutes_ready` | Cinco minutos. Bora? | Five minutes. Ready? |
| `v1.landing.no_sign_up_save_your_progress_later_if_y` | Sem cadastro. Você salva o progresso depois, se quiser. | No sign-up. Save your progress later if you want. |
| `v1.landing.caramelcase` | caramelCase | caramelCase |
| `v1.landing.portugu_s_brasil_english` | Português (Brasil) · English | Português (Brasil) · English |

### v1.onboarding-1 · Onboarding · step 1

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.onboarding-1.step_1_of_4` | etapa 1 de 4 | step 1 of 4 |
| `v1.onboarding-1.which_language_do_you_want_to_practice_i` | Em que idioma você quer praticar? | Which language do you want to practice in? |
| `v1.onboarding-1.you_can_change_it_later_in_settings` | Dá pra trocar depois em Ajustes. | You can change it later in Settings. |
| `v1.onboarding-1.language` | Idioma | Language |
| `v1.onboarding-1.portugu_s_brasil` | Português (Brasil) | Português (Brasil) |
| `v1.onboarding-1.english` | English | English |

### v1.onboarding-2 · Onboarding · step 2

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.onboarding-2.step_2_of_4` | etapa 2 de 4 | step 2 of 4 |
| `v1.onboarding-2.where_do_you_study` | Onde você estuda? | Where do you study? |
| `v1.onboarding-2.optional_it_helps_suggest_the_subjects_i` | Opcional. Ajuda a sugerir as matérias do seu curso. | Optional. It helps suggest the subjects in your course. |
| `v1.onboarding-2.university` | Universidade | University |
| `v1.onboarding-2.your_university` | Sua universidade | Your university |
| `v1.onboarding-2.course` | Curso | Course |
| `v1.onboarding-2.e_g_computer_science` | Ex.: Ciência da Computação | E.g. Computer Science |

### v1.onboarding-3 · Onboarding · step 3

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.onboarding-3.step_3_of_4` | etapa 3 de 4 | step 3 of 4 |
| `v1.onboarding-3.where_do_you_want_to_start` | Por onde quer começar? | Where do you want to start? |
| `v1.onboarding-3.you_can_switch_subjects_any_time` | Dá pra trocar de matéria quando quiser. | You can switch subjects any time. |
| `v1.onboarding-3.subject` | Matéria | Subject |

### v1.onboarding-4 · Onboarding · step 4

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.onboarding-4.step_4_of_4` | etapa 4 de 4 | step 4 of 4 |
| `v1.onboarding-4.what_s_your_daily_goal` | Qual é a sua meta diária? | What's your daily goal? |
| `v1.onboarding-4.a_session_has_about_10_questions_and_tak` | Uma sessão tem cerca de 10 questões e leva uns cinco minutos. | A session has about 10 questions and takes around five minutes. |
| `v1.onboarding-4.daily_goal` | Meta diária | Daily goal |
| `v1.onboarding-4.10_questions_a_day` | 10 questões por dia | 10 questions a day |
| `v1.onboarding-4.one_session_about_5_min` | Uma sessão · cerca de 5 min | One session · about 5 min |
| `v1.onboarding-4.20_questions_a_day` | 20 questões por dia | 20 questions a day |
| `v1.onboarding-4.two_sessions_about_10_min` | Duas sessões · cerca de 10 min | Two sessions · about 10 min |
| `v1.onboarding-4.30_questions_a_day` | 30 questões por dia | 30 questions a day |
| `v1.onboarding-4.three_sessions_about_15_min` | Três sessões · cerca de 15 min | Three sessions · about 15 min |

### v1.home · Home

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.home.today_s_goal_met` | Meta de hoje batida | Today's goal met |
| `v1.home.rating_algorithms` | rating · algoritmos | rating · algorithms |
| `v1.home.it_went_up_harder_questions_are_coming` | Subiu. Vêm questões mais difíceis. | It went up. Harder questions are coming. |

### v1.profile · Profile and stats

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.profile.carol_nunes` | Carol Nunes | Carol Nunes |
| `v1.profile.computer_science_your_university` | Ciência da Computação · Sua universidade | Computer Science · Your university |
| `v1.profile.questions` | questões | questions |
| `v1.profile.accuracy` | acertos | accuracy |
| `v1.profile.sessions` | sessões | sessions |
| `v1.profile.best_streak` | melhor sequência | best streak |
| `v1.profile.12_days` | 12 dias | 12 days |
| `v1.profile.rating_by_subject` | Rating por matéria | Rating by subject |
| `v1.profile.not_practiced_yet` | Ainda não praticou | Not practiced yet |
| `v1.profile.mastery_by_topic` | Domínio por tópico | Mastery by topic |
| `v1.profile.data_structures` | estruturas de dados | data structures |
| `v1.profile.calendar` | Calendário | Calendar |
| `v1.profile.november_2026` | novembro de 2026 | November 2026 |
| `v1.profile.day_with_practice` | dia com prática | day with practice |
| `v1.profile.today` | hoje | today |

### v1.signin · Sign in

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.signin.sign_in_to_caramelcase` | Entrar no caramelCase | Sign in to caramelCase |
| `v1.signin.keep_your_streak_your_rating_and_your_to` | Guarde sua sequência, seu rating e os tópicos pra revisar. | Keep your streak, your rating and your topics to review. |
| `v1.signin.continue_with_google` | Continuar com Google | Continue with Google |
| `v1.signin.or` | ou | or |
| `v1.signin.email` | E-mail | Email |
| `v1.signin.you_email_com` | voce@email.com | you@email.com |
| `v1.signin.we_ll_send_a_magic_link_no_password` | Mandamos um link mágico. Sem senha. | We'll send a magic link. No password. |
| `v1.signin.send_magic_link` | Enviar link mágico | Send magic link |
| `v1.signin.continue_without_an_account` | Continuar sem conta | Continue without an account |

### v1.settings · Settings

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.settings.language` | Idioma | Language |
| `v1.settings.portugu_s_brasil` | Português (Brasil) | Português (Brasil) |
| `v1.settings.english` | English | English |
| `v1.settings.theme` | Tema | Theme |
| `v1.settings.light` | Claro | Light |
| `v1.settings.dark` | Escuro | Dark |
| `v1.settings.system` | Sistema | System |
| `v1.settings.session` | Sessão | Session |
| `v1.settings.explain_every_option` | Explicar cada alternativa | Explain every option |
| `v1.settings.shows_the_reason_under_each_option_after` | Mostra o porquê embaixo de cada opção depois de responder. | Shows the reason under each option after you answer. |
| `v1.settings.notifications` | Notificações | Notifications |
| `v1.settings.daily_reminder` | Lembrete diário | Daily reminder |
| `v1.settings.a_nudge_if_you_haven_t_practiced_today` | Um aviso se você ainda não praticou hoje. | A nudge if you haven't practiced today. |
| `v1.settings.account` | Conta | Account |
| `v1.settings.carol_email_com` | carol@email.com | carol@email.com |
| `v1.settings.sign_out` | Sair | Sign out |
| `v1.settings.delete_account` | Excluir conta | Delete account |
| `v1.settings.deletes_your_account_and_your_progress_t` | Apaga sua conta e seu progresso. Não dá pra desfazer. | Deletes your account and your progress. This can't be undone. |

### v1.signin-sent · Sign in · link sent

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.signin-sent.check_your_email` | Olha seu e-mail | Check your email |
| `v1.signin-sent.we_sent_a_link_to_carol_email_com_open_i` | Mandamos um link pra carol@email.com. Abra neste aparelho pra entrar. | We sent a link to carol@email.com. Open it on this device to sign in. |
| `v1.signin-sent.resend_link` | Reenviar link | Resend link |
| `v1.signin-sent.use_another_email` | Usar outro e-mail | Use another email |

### v1.settings-delete · Settings · delete account

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.settings-delete.language` | Idioma | Language |
| `v1.settings-delete.portugu_s_brasil` | Português (Brasil) | Português (Brasil) |
| `v1.settings-delete.english` | English | English |
| `v1.settings-delete.theme` | Tema | Theme |
| `v1.settings-delete.light` | Claro | Light |
| `v1.settings-delete.dark` | Escuro | Dark |
| `v1.settings-delete.system` | Sistema | System |
| `v1.settings-delete.session` | Sessão | Session |
| `v1.settings-delete.explain_every_option` | Explicar cada alternativa | Explain every option |
| `v1.settings-delete.shows_the_reason_under_each_option_after` | Mostra o porquê embaixo de cada opção depois de responder. | Shows the reason under each option after you answer. |
| `v1.settings-delete.notifications` | Notificações | Notifications |
| `v1.settings-delete.daily_reminder` | Lembrete diário | Daily reminder |
| `v1.settings-delete.a_nudge_if_you_haven_t_practiced_today` | Um aviso se você ainda não praticou hoje. | A nudge if you haven't practiced today. |
| `v1.settings-delete.account` | Conta | Account |
| `v1.settings-delete.carol_email_com` | carol@email.com | carol@email.com |
| `v1.settings-delete.sign_out` | Sair | Sign out |
| `v1.settings-delete.delete_account` | Excluir conta | Delete account |
| `v1.settings-delete.deletes_your_account_and_your_progress_t` | Apaga sua conta e seu progresso. Não dá pra desfazer. | Deletes your account and your progress. This can't be undone. |
| `v1.settings-delete.delete_your_account` | Excluir sua conta? | Delete your account? |
| `v1.settings-delete.this_deletes_your_progress_your_streak_a` | Isso apaga seu progresso, sua sequência e seu rating. Não dá pra desfazer. | This deletes your progress, your streak and your rating. It can't be undone. |
| `v1.settings-delete.cancel` | Cancelar | Cancel |

### v1.flow-first-1 · First session · tap 1, pick an option

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-first-1.language_english` | Idioma: Português (Brasil) | Language: English |
| `v1.flow-first-1.en` | PT-BR | EN |
| `v1.flow-first-1.sign_in` | Entrar | Sign in |
| `v1.flow-first-1.try_it_answer_without_an_account` | // experimente: responda sem criar conta | // try it: answer without an account |
| `v1.flow-first-1.queue` | Fila | Queue |
| `v1.flow-first-1.stack` | Pilha | Stack |
| `v1.flow-first-1.linked_list` | Lista ligada | Linked list |
| `v1.flow-first-1.binary_tree` | Árvore binária | Binary tree |

### v1.flow-first-2 · First session · tap 2, answered

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-first-2.language_english` | Idioma: Português (Brasil) | Language: English |
| `v1.flow-first-2.en` | PT-BR | EN |
| `v1.flow-first-2.sign_in` | Entrar | Sign in |
| `v1.flow-first-2.try_it_answer_without_an_account` | // experimente: responda sem criar conta | // try it: answer without an account |
| `v1.flow-first-2.queue` | Fila | Queue |
| `v1.flow-first-2.a_queue_does_the_opposite_it_s_fifo_the` | A fila faz o contrário: é FIFO, o primeiro a entrar sai primeiro. | A queue does the opposite: it's FIFO, the first in is the first out. |
| `v1.flow-first-2.stack` | Pilha | Stack |
| `v1.flow-first-2.correct` | Correta | Correct |
| `v1.flow-first-2.the_last_in_is_the_first_out_like_a_stac` | O último a entrar é o primeiro a sair, como uma pilha de pratos. | The last in is the first out, like a stack of plates. |
| `v1.flow-first-2.linked_list` | Lista ligada | Linked list |
| `v1.flow-first-2.it_allows_inserting_and_removing_at_any` | Permite inserir e remover em qualquer posição; não impõe LIFO. | It allows inserting and removing at any position; it doesn't enforce LIFO. |
| `v1.flow-first-2.binary_tree` | Árvore binária | Binary tree |
| `v1.flow-first-2.it_organises_data_as_a_hierarchy_not_by` | Organiza os dados em hierarquia, não por ordem de chegada. | It organises data as a hierarchy, not by order of arrival. |
| `v1.flow-first-2.keep_practicing` | Continuar praticando | Keep practicing |

### v1.state-loading · System state · loading

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.state-loading.mel_thinking` | Mel pensando | Mel thinking |
| `v1.state-loading.loading` | Carregando… | Loading… |

### v1.state-empty · System state · empty

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.state-empty.nothing_here_yet` | Nada por aqui ainda | Nothing here yet |
| `v1.state-empty.do_your_first_session_and_your_numbers_w` | Faça sua primeira sessão e seus números aparecem aqui. | Do your first session and your numbers will show up here. |

### v1.state-offline · System state · offline

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.state-offline.no_connection` | Sem conexão | No connection |
| `v1.state-offline.check_your_internet_what_you_ve_already` | Confira sua internet. O que você já respondeu está salvo neste aparelho. | Check your internet. What you've already answered is saved on this device. |
| `v1.state-offline.try_again` | Tentar de novo | Try again |

### v1.state-error · System state · error

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.state-error.something_went_wrong` | Algo deu errado | Something went wrong |
| `v1.state-error.it_wasn_t_you_it_was_us_try_again_in_a_m` | Não foi você, foi a gente. Tenta de novo daqui a pouco. | It wasn't you, it was us. Try again in a moment. |
| `v1.state-error.try_again` | Tentar de novo | Try again |

### v1.state-404 · System state · 404

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.state-404.mel_looking_mischievous` | Mel com cara de travesso | Mel looking mischievous |
| `v1.state-404.pagenotfound_404` | PaginaNaoEncontrada: 404 | PageNotFound: 404 |
| `v1.state-404.this_page_ran_off` | Essa página fugiu | This page ran off |
| `v1.state-404.the_link_may_be_wrong_or_the_page_has_mo` | O link pode estar errado ou a página mudou de lugar. | The link may be wrong or the page has moved. |

### v1.state-maintenance · System state · maintenance

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.state-maintenance.mel_in_glasses_at_a_laptop` | Mel de óculos no laptop | Mel in glasses at a laptop |
| `v1.state-maintenance.git_commit_m_tidying_up` | git commit -m "arrumando a casa" | git commit -m "tidying up" |
| `v1.state-maintenance.under_maintenance` | Em manutenção | Under maintenance |
| `v1.state-maintenance.we_re_fixing_a_few_things_back_soon` | Estamos arrumando umas coisas. Volta já. | We're fixing a few things. Back soon. |

### v1.flow-streak · Streak lifecycle

| Key | PT-BR | EN |
| --- | --- | --- |
| `v1.flow-streak.streak` | Sequência | Streak |
| `v1.flow-streak.the_five_moments_as_they_appear_at_the_t` | Os cinco momentos, como aparecem no topo do Início. | The five moments, as they appear at the top of Home. |
| `v1.flow-streak.started` | começou | started |
| `v1.flow-streak.1_day` | 1 dia | 1 day |
| `v1.flow-streak.started_today` | Começou hoje | Started today |
| `v1.flow-streak.your_streak_has_started_come_back_tomorr` | Sua sequência começou. Volte amanhã pra manter. | Your streak has started. Come back tomorrow to keep it. |
| `v1.flow-streak.extended` | continuou | extended |
| `v1.flow-streak.today_s_goal_met` | Meta de hoje batida | Today's goal met |
| `v1.flow-streak.one_more_day_nailed_it` | Mais um dia. Mandou bem! | One more day. Nailed it! |
| `v1.flow-streak.at_risk_today` | em risco hoje | at risk today |
| `v1.flow-streak.mel_thinking` | Mel pensando | Mel thinking |
| `v1.flow-streak.practice_today_to_keep_it` | Pratique hoje pra não perder | Practice today to keep it |
| `v1.flow-streak.your_7_day_streak_ends_tonight_at_midnig` | Sua sequência de 7 dias acaba hoje à meia-noite. | Your 7-day streak ends tonight at midnight. |
| `v1.flow-streak.practice_now` | Praticar agora | Practice now |
| `v1.flow-streak.lost` | perdida | lost |
| `v1.flow-streak.streak_lost` | Sequência perdida | Streak lost |
| `v1.flow-streak.start_a_new_one` | Bora começar outra? | Start a new one? |
| `v1.flow-streak.your_7_day_streak_ended_it_happens_start` | Sua sequência de 7 dias terminou. Acontece. Bora começar outra? | Your 7-day streak ended. It happens. Start a new one? |
| `v1.flow-streak.restored_arrives_with_v2_freeze_and_v3_r` | recuperada · chega com o V2 (congelamento) e o V3 (reparo) | restored · arrives with V2 (freeze) and V3 (repair) |
| `v1.flow-streak.streak_restored` | Sequência recuperada | Streak restored |
| `v1.flow-streak.streak_restored_your_7_days_carry_on` | Sequência recuperada. Seus 7 dias continuam. | Streak restored. Your 7 days carry on. |

## V2

### v2.review · Review queue

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.review.for_today` | pra hoje | for today |
| `v2.review.questions_to_review` | questões pra revisar | questions to review |
| `v2.review.these_are_the_ones_you_missed_coming_bac` | São as que você errou, voltando bem na hora de não esquecer. | These are the ones you missed, coming back just in time so you don't forget. |
| `v2.review.start_review` | Começar revisão | Start review |
| `v2.review.what_s_back_today` | O que volta hoje | What's back today |
| `v2.review.5_questions` | 5 questões | 5 questions |
| `v2.review.4_questions` | 4 questões | 4 questions |
| `v2.review.3_questions` | 3 questões | 3 questions |
| `v2.review.coming_up` | Próximas | Coming up |
| `v2.review.tomorrow` | Amanhã | Tomorrow |
| `v2.review.6_questions` | 6 questões | 6 questions |
| `v2.review.in_3_days` | Em 3 dias | In 3 days |
| `v2.review.9_questions` | 9 questões | 9 questions |
| `v2.review.in_7_days` | Em 7 dias | In 7 days |
| `v2.review.14_questions` | 14 questões | 14 questions |

### v2.type-1-truefalse · True or false

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.type-1-truefalse.true_or_false` | verdadeiro ou falso | true or false |
| `v2.type-1-truefalse.in_a_queue_the_first_element_in_is_the_f` | Em uma fila, o primeiro elemento a entrar é o primeiro a sair. | In a queue, the first element in is the first one out. |
| `v2.type-1-truefalse.answer` | Resposta | Answer |
| `v2.type-1-truefalse.true` | Verdadeiro | True |
| `v2.type-1-truefalse.false` | Falso | False |
| `v2.type-1-truefalse.keys_1_and_2_select_enter_checks` | Teclas 1 e 2 escolhem · Enter verifica | Keys 1 and 2 select · Enter checks |

### v2.type-2-predict · Predict the output

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.type-2-predict.predict_the_output` | prever a saída | predict the output |
| `v2.type-2-predict.output` | saída | output |
| `v2.type-2-predict.keys_1_to_4_select_enter_checks` | Teclas 1 a 4 escolhem · Enter verifica | Keys 1 to 4 select · Enter checks |

### v2.type-3-bug · Find the bug

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.type-3-bug.loops` | Laços | Loops |
| `v2.type-3-bug.find_the_bug` | ache o bug | find the bug |
| `v2.type-3-bug.this_function_should_add_up_every_elemen` | Esta função deveria somar todos os elementos do vetor. Toque na linha com o bug. | This function should add up every element of the list. Tap the line with the bug. |
| `v2.type-3-bug.arrows_pick_the_line_enter_checks` | Setas escolhem a linha · Enter verifica | Arrows pick the line · Enter checks |

### v2.type-4-blank · Fill in the blank

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.type-4-blank.fill_in_the_blank` | preencha a lacuna | fill in the blank |
| `v2.type-4-blank.complete_the_recursive_function_that_com` | Complete a função recursiva que calcula o fatorial. | Complete the recursive function that computes the factorial. |
| `v2.type-4-blank.tap_an_option_to_fill_the_blank_tap_the` | Toque numa opção pra preencher a lacuna. Toque na lacuna pra limpar. | Tap an option to fill the blank. Tap the blank to clear it. |
| `v2.type-4-blank.fatorial_n` | fatorial(n) | fatorial(n) |
| `v2.type-4-blank.fatorial_n_1` | fatorial(n - 1) | fatorial(n - 1) |
| `v2.type-4-blank.n_1` | n - 1 | n - 1 |
| `v2.type-4-blank.fatorial_n_1_2` | fatorial(n + 1) | fatorial(n + 1) |
| `v2.type-4-blank.keys_1_to_4_fill_enter_checks` | Teclas 1 a 4 preenchem · Enter verifica | Keys 1 to 4 fill · Enter checks |

### v2.type-5-order · Order the steps

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.type-5-order.order_the_steps` | ordene os passos | order the steps |
| `v2.type-5-order.put_the_steps_of_binary_search_in_order` | Coloque os passos da busca binária em ordem. | Put the steps of binary search in order. |
| `v2.type-5-order.drag_by_the_handle_or_use_each_step_s_ar` | Arraste pelo pegador ou use as setas de cada passo. | Drag by the handle or use each step's arrows. |
| `v2.type-5-order.steps` | Passos | Steps |
| `v2.type-5-order.look_at_the_middle_element` | Olhe o elemento do meio | Look at the middle element |
| `v2.type-5-order.move_step_1_up` | Subir passo 1 | Move step 1 up |
| `v2.type-5-order.move_step_1_down` | Descer passo 1 | Move step 1 down |
| `v2.type-5-order.discard_the_half_where_the_target_cannot` | Descarte a metade onde o alvo não pode estar | Discard the half where the target cannot be |
| `v2.type-5-order.move_step_2_up` | Subir passo 2 | Move step 2 up |
| `v2.type-5-order.move_step_2_down` | Descer passo 2 | Move step 2 down |
| `v2.type-5-order.if_it_s_the_target_stop` | Se for o alvo, pare | If it's the target, stop |
| `v2.type-5-order.move_step_3_up` | Subir passo 3 | Move step 3 up |
| `v2.type-5-order.move_step_3_down` | Descer passo 3 | Move step 3 down |
| `v2.type-5-order.repeat_on_the_half_that_s_left` | Repita na metade que sobrou | Repeat on the half that's left |
| `v2.type-5-order.move_step_4_up` | Subir passo 4 | Move step 4 up |
| `v2.type-5-order.move_step_4_down` | Descer passo 4 | Move step 4 down |
| `v2.type-5-order.tab_picks_a_step_arrows_move_it_enter_ch` | Tab escolhe um passo · setas movem · Enter verifica | Tab picks a step · arrows move it · Enter checks |

### v2.exam-1-question · Exam mode · question

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.exam-1-question.leave_exam` | Sair da prova | Leave exam |
| `v2.exam-1-question.mock_exam` | Simulado | Mock exam |
| `v2.exam-1-question.exam_mode` | modo prova | exam mode |
| `v2.exam-1-question.mel_studying` | Mel estudando | Mel studying |
| `v2.exam-1-question.in_exam_mode_answers_are_only_checked_at` | No modo prova, a correção só aparece no final. | In exam mode, answers are only checked at the end. |
| `v2.exam-1-question.flag_for_review` | Marcar pra revisar | Flag for review |
| `v2.exam-1-question.open_question_list` | Abrir lista de questões | Open question list |
| `v2.exam-1-question.previous` | Anterior | Previous |
| `v2.exam-1-question.next` | Próxima | Next |
| `v2.exam-1-question.question_1_answered` | Questão 1, respondida | Question 1, answered |
| `v2.exam-1-question.question_2_answered` | Questão 2, respondida | Question 2, answered |
| `v2.exam-1-question.question_3_answered` | Questão 3, respondida | Question 3, answered |
| `v2.exam-1-question.question_4_answered` | Questão 4, respondida | Question 4, answered |
| `v2.exam-1-question.question_5_blank` | Questão 5, em branco | Question 5, blank |
| `v2.exam-1-question.question_6_answered` | Questão 6, respondida | Question 6, answered |
| `v2.exam-1-question.question_7_answered` | Questão 7, respondida | Question 7, answered |
| `v2.exam-1-question.question_8_flagged` | Questão 8, marcada | Question 8, flagged |
| `v2.exam-1-question.question_9_answered` | Questão 9, respondida | Question 9, answered |
| `v2.exam-1-question.question_10_answered` | Questão 10, respondida | Question 10, answered |
| `v2.exam-1-question.question_11_answered` | Questão 11, respondida | Question 11, answered |
| `v2.exam-1-question.question_12_current` | Questão 12, atual | Question 12, current |
| `v2.exam-1-question.question_13_blank` | Questão 13, em branco | Question 13, blank |
| `v2.exam-1-question.question_14_blank` | Questão 14, em branco | Question 14, blank |
| `v2.exam-1-question.question_15_blank` | Questão 15, em branco | Question 15, blank |
| `v2.exam-1-question.question_16_blank` | Questão 16, em branco | Question 16, blank |
| `v2.exam-1-question.question_17_blank` | Questão 17, em branco | Question 17, blank |
| `v2.exam-1-question.question_18_blank` | Questão 18, em branco | Question 18, blank |
| `v2.exam-1-question.question_19_blank` | Questão 19, em branco | Question 19, blank |
| `v2.exam-1-question.question_20_blank` | Questão 20, em branco | Question 20, blank |
| `v2.exam-1-question.question_21_blank` | Questão 21, em branco | Question 21, blank |
| `v2.exam-1-question.question_22_blank` | Questão 22, em branco | Question 22, blank |
| `v2.exam-1-question.question_23_blank` | Questão 23, em branco | Question 23, blank |
| `v2.exam-1-question.question_24_blank` | Questão 24, em branco | Question 24, blank |
| `v2.exam-1-question.question_25_blank` | Questão 25, em branco | Question 25, blank |
| `v2.exam-1-question.question_26_blank` | Questão 26, em branco | Question 26, blank |
| `v2.exam-1-question.question_27_blank` | Questão 27, em branco | Question 27, blank |
| `v2.exam-1-question.question_28_blank` | Questão 28, em branco | Question 28, blank |
| `v2.exam-1-question.question_29_blank` | Questão 29, em branco | Question 29, blank |
| `v2.exam-1-question.question_30_blank` | Questão 30, em branco | Question 30, blank |
| `v2.exam-1-question.question_31_blank` | Questão 31, em branco | Question 31, blank |
| `v2.exam-1-question.question_32_blank` | Questão 32, em branco | Question 32, blank |
| `v2.exam-1-question.question_33_blank` | Questão 33, em branco | Question 33, blank |
| `v2.exam-1-question.question_34_blank` | Questão 34, em branco | Question 34, blank |
| `v2.exam-1-question.question_35_blank` | Questão 35, em branco | Question 35, blank |
| `v2.exam-1-question.question_36_blank` | Questão 36, em branco | Question 36, blank |
| `v2.exam-1-question.question_37_blank` | Questão 37, em branco | Question 37, blank |
| `v2.exam-1-question.question_38_blank` | Questão 38, em branco | Question 38, blank |
| `v2.exam-1-question.question_39_blank` | Questão 39, em branco | Question 39, blank |
| `v2.exam-1-question.question_40_blank` | Questão 40, em branco | Question 40, blank |
| `v2.exam-1-question.answered` | respondida | answered |
| `v2.exam-1-question.current` | atual | current |
| `v2.exam-1-question.flagged` | marcada | flagged |
| `v2.exam-1-question.blank` | em branco | blank |
| `v2.exam-1-question.10_answered_1_flagged_29_blank` | 10 respondidas · 1 marcada · 29 em branco | 10 answered · 1 flagged · 29 blank |
| `v2.exam-1-question.submit_exam` | Entregar prova | Submit exam |

### v2.exam-3-results · Exam mode · results by topic

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.exam-3-results.mel_in_glasses_at_a_laptop` | Mel de óculos no laptop | Mel in glasses at a laptop |
| `v2.exam-3-results.mock_exam_complete` | Simulado concluído | Mock exam complete |
| `v2.exam-3-results.out_of_40_correct` | de 40 certas | out of 40 correct |
| `v2.exam-3-results.accuracy` | acertos | accuracy |
| `v2.exam-3-results.time` | tempo | time |
| `v2.exam-3-results.blank` | em branco | blank |
| `v2.exam-3-results.by_topic` | Por tópico | By topic |
| `v2.exam-3-results.7_of_8` | 7 de 8 | 7 of 8 |
| `v2.exam-3-results.sorting` | Ordenação | Sorting |
| `v2.exam-3-results.8_of_10` | 8 de 10 | 8 of 10 |
| `v2.exam-3-results.6_of_10` | 6 de 10 | 6 of 10 |
| `v2.exam-3-results.4_of_7` | 4 de 7 | 4 of 7 |
| `v2.exam-3-results.complexity` | Complexidade | Complexity |
| `v2.exam-3-results.4_of_5` | 4 de 5 | 4 of 5 |
| `v2.exam-3-results.review_answers` | Revisar respostas | Review answers |

### v2.leagues · Leagues

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.leagues.byte_league` | Liga Byte | Byte League |
| `v2.leagues.ends_in_3_days_you_re_in_4th` | Termina em 3 dias. Você está em 4º. | Ends in 3 days. You're in 4th. |
| `v2.leagues.the_top_3_move_up_to_kilobyte_league_the` | Os 3 primeiros sobem pra Liga Kilobyte. Os 3 últimos descem pra Liga Bit. | The top 3 move up to Kilobyte League. The bottom 3 move down to Bit League. |
| `v2.leagues.promotion_zone` | zona de promoção | promotion zone |
| `v2.leagues.ana_l` | Ana L. | Ana L. |
| `v2.leagues.rafael_m` | Rafael M. | Rafael M. |
| `v2.leagues.bia_s` | Bia S. | Bia S. |
| `v2.leagues.carol_n` | Carol N. | Carol N. |
| `v2.leagues.you` | Você | You |
| `v2.leagues.diego_f` | Diego F. | Diego F. |
| `v2.leagues.l_via_r` | Lívia R. | Lívia R. |
| `v2.leagues.tiago_p` | Tiago P. | Tiago P. |
| `v2.leagues.relegation_zone` | zona de rebaixamento | relegation zone |
| `v2.leagues.marina_c` | Marina C. | Marina C. |
| `v2.leagues.pedro_a` | Pedro A. | Pedro A. |
| `v2.leagues.j_lia_t` | Júlia T. | Júlia T. |

### v2.achievements · Achievements

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.achievements.achievements` | Conquistas | Achievements |
| `v2.achievements.4_of_9_unlocked` | 4 de 9 conquistadas | 4 of 9 unlocked |
| `v2.achievements.first_session` | Primeira sessão | First session |
| `v2.achievements.unlocked` | Conquistada | Unlocked |
| `v2.achievements.100_questions` | 100 questões | 100 questions |
| `v2.achievements.new` | Nova! | New! |
| `v2.achievements.goal_met_7_times` | Meta batida 7 vezes | Goal met 7 times |
| `v2.achievements.level_5` | Nível 5 | Level 5 |
| `v2.achievements.locked` | Bloqueada | Locked |
| `v2.achievements.30_day_streak` | 30 dias seguidos | 30-day streak |
| `v2.achievements.rating_1500` | Rating 1500 | Rating 1500 |
| `v2.achievements.first_mock_exam` | Primeiro simulado | First mock exam |
| `v2.achievements.kilobyte_league` | Liga Kilobyte | Kilobyte League |

### v2.lives-out · Out of lives

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.lives-out.0_of_3_lives` | 0 de 3 vidas | 0 of 3 lives |
| `v2.lives-out.out_of_lives` | Acabaram as vidas | Out of lives |
| `v2.lives-out.next_life_in_24_10` | Próxima vida em 24:10 | Next life in 24:10 |
| `v2.lives-out.how_lives_come_back` | Como as vidas voltam | How lives come back |
| `v2.lives-out.one_life_every_30_minutes` | Uma vida a cada 30 minutos | One life every 30 minutes |
| `v2.lives-out.they_refill_on_their_own_up_to_3` | Elas voltam sozinhas, até o máximo de 3. | They refill on their own, up to 3. |
| `v2.lives-out.review_doesn_t_cost_lives` | Revisão não gasta vidas | Review doesn't cost lives |
| `v2.lives-out.you_can_do_your_reviews_while_you_wait` | Dá pra praticar suas revisões enquanto espera. | You can do your reviews while you wait. |
| `v2.lives-out.do_a_review` | Fazer revisão | Do a review |

### v2.catalog · Subject catalog

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.catalog.subjects` | Matérias | Subjects |
| `v2.catalog.search_subjects` | Buscar matéria | Search subjects |
| `v2.catalog.filter_by_course` | filtrar por curso | filter by course |
| `v2.catalog.all` | Todos | All |
| `v2.catalog.computer_science` | Ciência da Computação | Computer Science |
| `v2.catalog.information_systems` | Sistemas de Informação | Information Systems |
| `v2.catalog.software_engineering` | Engenharia de Software | Software Engineering |
| `v2.catalog.your_subjects` | Suas matérias | Your subjects |
| `v2.catalog.remove` | Remover | Remove |
| `v2.catalog.alg` | alg/ | alg/ |
| `v2.catalog.other_subjects` | Outras matérias | Other subjects |
| `v2.catalog.os` | so/ | os/ |
| `v2.catalog.add` | Adicionar | Add |
| `v2.catalog.db` | bd/ | db/ |
| `v2.catalog.net` | redes/ | net/ |

### v2.review-empty · Review queue · empty

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.review-empty.all_reviewed_for_today` | Tudo revisado por hoje | All reviewed for today |
| `v2.review-empty.your_next_review_arrives_tomorrow_with_6` | Sua próxima revisão chega amanhã, com 6 questões. | Your next review arrives tomorrow, with 6 questions. |

### v2.exam-2-navigator · Exam mode · question navigator

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.exam-2-navigator.leave_exam` | Sair da prova | Leave exam |
| `v2.exam-2-navigator.mock_exam` | Simulado | Mock exam |
| `v2.exam-2-navigator.exam_mode` | modo prova | exam mode |
| `v2.exam-2-navigator.mel_studying` | Mel estudando | Mel studying |
| `v2.exam-2-navigator.in_exam_mode_answers_are_only_checked_at` | No modo prova, a correção só aparece no final. | In exam mode, answers are only checked at the end. |
| `v2.exam-2-navigator.flag_for_review` | Marcar pra revisar | Flag for review |
| `v2.exam-2-navigator.open_question_list` | Abrir lista de questões | Open question list |
| `v2.exam-2-navigator.previous` | Anterior | Previous |
| `v2.exam-2-navigator.next` | Próxima | Next |
| `v2.exam-2-navigator.question_1_answered` | Questão 1, respondida | Question 1, answered |
| `v2.exam-2-navigator.question_2_answered` | Questão 2, respondida | Question 2, answered |
| `v2.exam-2-navigator.question_3_answered` | Questão 3, respondida | Question 3, answered |
| `v2.exam-2-navigator.question_4_answered` | Questão 4, respondida | Question 4, answered |
| `v2.exam-2-navigator.question_5_blank` | Questão 5, em branco | Question 5, blank |
| `v2.exam-2-navigator.question_6_answered` | Questão 6, respondida | Question 6, answered |
| `v2.exam-2-navigator.question_7_answered` | Questão 7, respondida | Question 7, answered |
| `v2.exam-2-navigator.question_8_flagged` | Questão 8, marcada | Question 8, flagged |
| `v2.exam-2-navigator.question_9_answered` | Questão 9, respondida | Question 9, answered |
| `v2.exam-2-navigator.question_10_answered` | Questão 10, respondida | Question 10, answered |
| `v2.exam-2-navigator.question_11_answered` | Questão 11, respondida | Question 11, answered |
| `v2.exam-2-navigator.question_12_current` | Questão 12, atual | Question 12, current |
| `v2.exam-2-navigator.question_13_blank` | Questão 13, em branco | Question 13, blank |
| `v2.exam-2-navigator.question_14_blank` | Questão 14, em branco | Question 14, blank |
| `v2.exam-2-navigator.question_15_blank` | Questão 15, em branco | Question 15, blank |
| `v2.exam-2-navigator.question_16_blank` | Questão 16, em branco | Question 16, blank |
| `v2.exam-2-navigator.question_17_blank` | Questão 17, em branco | Question 17, blank |
| `v2.exam-2-navigator.question_18_blank` | Questão 18, em branco | Question 18, blank |
| `v2.exam-2-navigator.question_19_blank` | Questão 19, em branco | Question 19, blank |
| `v2.exam-2-navigator.question_20_blank` | Questão 20, em branco | Question 20, blank |
| `v2.exam-2-navigator.question_21_blank` | Questão 21, em branco | Question 21, blank |
| `v2.exam-2-navigator.question_22_blank` | Questão 22, em branco | Question 22, blank |
| `v2.exam-2-navigator.question_23_blank` | Questão 23, em branco | Question 23, blank |
| `v2.exam-2-navigator.question_24_blank` | Questão 24, em branco | Question 24, blank |
| `v2.exam-2-navigator.question_25_blank` | Questão 25, em branco | Question 25, blank |
| `v2.exam-2-navigator.question_26_blank` | Questão 26, em branco | Question 26, blank |
| `v2.exam-2-navigator.question_27_blank` | Questão 27, em branco | Question 27, blank |
| `v2.exam-2-navigator.question_28_blank` | Questão 28, em branco | Question 28, blank |
| `v2.exam-2-navigator.question_29_blank` | Questão 29, em branco | Question 29, blank |
| `v2.exam-2-navigator.question_30_blank` | Questão 30, em branco | Question 30, blank |
| `v2.exam-2-navigator.question_31_blank` | Questão 31, em branco | Question 31, blank |
| `v2.exam-2-navigator.question_32_blank` | Questão 32, em branco | Question 32, blank |
| `v2.exam-2-navigator.question_33_blank` | Questão 33, em branco | Question 33, blank |
| `v2.exam-2-navigator.question_34_blank` | Questão 34, em branco | Question 34, blank |
| `v2.exam-2-navigator.question_35_blank` | Questão 35, em branco | Question 35, blank |
| `v2.exam-2-navigator.question_36_blank` | Questão 36, em branco | Question 36, blank |
| `v2.exam-2-navigator.question_37_blank` | Questão 37, em branco | Question 37, blank |
| `v2.exam-2-navigator.question_38_blank` | Questão 38, em branco | Question 38, blank |
| `v2.exam-2-navigator.question_39_blank` | Questão 39, em branco | Question 39, blank |
| `v2.exam-2-navigator.question_40_blank` | Questão 40, em branco | Question 40, blank |
| `v2.exam-2-navigator.answered` | respondida | answered |
| `v2.exam-2-navigator.current` | atual | current |
| `v2.exam-2-navigator.flagged` | marcada | flagged |
| `v2.exam-2-navigator.blank` | em branco | blank |
| `v2.exam-2-navigator.10_answered_1_flagged_29_blank` | 10 respondidas · 1 marcada · 29 em branco | 10 answered · 1 flagged · 29 blank |
| `v2.exam-2-navigator.submit_exam` | Entregar prova | Submit exam |

### v2.achievements-unlock · Achievement · unlock moment

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.achievements-unlock.achievements` | Conquistas | Achievements |
| `v2.achievements-unlock.4_of_9_unlocked` | 4 de 9 conquistadas | 4 of 9 unlocked |
| `v2.achievements-unlock.first_session` | Primeira sessão | First session |
| `v2.achievements-unlock.unlocked` | Conquistada | Unlocked |
| `v2.achievements-unlock.100_questions` | 100 questões | 100 questions |
| `v2.achievements-unlock.new` | Nova! | New! |
| `v2.achievements-unlock.goal_met_7_times` | Meta batida 7 vezes | Goal met 7 times |
| `v2.achievements-unlock.level_5` | Nível 5 | Level 5 |
| `v2.achievements-unlock.locked` | Bloqueada | Locked |
| `v2.achievements-unlock.30_day_streak` | 30 dias seguidos | 30-day streak |
| `v2.achievements-unlock.rating_1500` | Rating 1500 | Rating 1500 |
| `v2.achievements-unlock.first_mock_exam` | Primeiro simulado | First mock exam |
| `v2.achievements-unlock.kilobyte_league` | Liga Kilobyte | Kilobyte League |
| `v2.achievements-unlock.achievement_unlocked` | conquista desbloqueada | achievement unlocked |
| `v2.achievements-unlock.a_hundred_questions_answered_ready_for_t` | Cem questões respondidas. Bora pras próximas cem? | A hundred questions answered. Ready for the next hundred? |

### v2.lives-session · Lives in the session header

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.lives-session.2_of_3_lives` | 2 de 3 vidas | 2 of 3 lives |

### v2.catalog-search · Subject catalog · search

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.catalog-search.subjects` | Matérias | Subjects |
| `v2.catalog-search.search_subjects` | Buscar matéria | Search subjects |
| `v2.catalog-search.filter_by_course` | filtrar por curso | filter by course |
| `v2.catalog-search.all` | Todos | All |
| `v2.catalog-search.computer_science` | Ciência da Computação | Computer Science |
| `v2.catalog-search.information_systems` | Sistemas de Informação | Information Systems |
| `v2.catalog-search.software_engineering` | Engenharia de Software | Software Engineering |
| `v2.catalog-search.1_result` | 1 resultado | 1 result |
| `v2.catalog-search.net` | redes/ | net/ |
| `v2.catalog-search.add` | Adicionar | Add |

### v2.freeze · Streak freeze

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.freeze.streak_freeze` | Congelamento de sequência | Streak freeze |
| `v2.freeze.an_earned_item_that_protects_your_streak` | Um item ganho que protege a sequência num dia sem prática. Ganha-se batendo a meta 7 dias seguidos; dá pra guardar até 2. | An earned item that protects your streak on a day without practice. Earn one by meeting your goal 7 days in a row; you can hold up to 2. |
| `v2.freeze.at_the_top_of_home_count_next_to_the_str` | no topo do início: contagem ao lado da sequência | at the top of Home: count next to the streak |
| `v2.freeze.1_freezes_held` | 1 congelamentos guardados | 1 freezes held |
| `v2.freeze.earned_one` | ganhou um | earned one |
| `v2.freeze.you_earned_a_streak_freeze` | Você ganhou um congelamento | You earned a streak freeze |
| `v2.freeze.goal_met_7_days_in_a_row` | Meta batida 7 dias seguidos. | Goal met 7 days in a row. |
| `v2.freeze.if_you_miss_a_day_it_kicks_in_on_its_own` | Se você faltar um dia, ele entra sozinho e sua sequência continua. | If you miss a day, it kicks in on its own and your streak carries on. |
| `v2.freeze.nice` | Boa! | Nice! |
| `v2.freeze.used` | usado | used |
| `v2.freeze.freeze_used_yesterday` | Congelamento usado ontem | Freeze used yesterday |
| `v2.freeze.your_7_days_carry_on_0_left` | Seus 7 dias continuam. Resta 0 guardado. | Your 7 days carry on. 0 left. |
| `v2.freeze.0_freezes_held` | 0 congelamentos guardados | 0 freezes held |
| `v2.freeze.at_the_maximum` | no máximo | at the maximum |
| `v2.freeze.2_of_2_held` | 2 de 2 guardados | 2 of 2 held |
| `v2.freeze.you_already_hold_the_maximum_the_next_on` | Você já tem o máximo. O próximo só conta depois de usar um. | You already hold the maximum. The next one only counts after you use one. |

### v2.notifications · Push notifications

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.notifications.push_notifications` | Notificações push | Push notifications |
| `v2.notifications.at_most_one_a_day_all_can_be_turned_off` | No máximo uma por dia. Todas desligam em Ajustes. | At most one a day. All can be turned off in Settings. |
| `v2.notifications.streak_reminder` | lembrete da sequência | streak reminder |
| `v2.notifications.caramelcase_icon` | Ícone do caramelCase | caramelCase icon |
| `v2.notifications.caramelcase` | caramelCase | caramelCase |
| `v2.notifications.now` | agora | now |
| `v2.notifications.your_7_day_streak_ends_today` | Sua sequência de 7 dias acaba hoje | Your 7-day streak ends today |
| `v2.notifications.five_minutes_will_do_it_ready` | Cinco minutos resolvem. Bora? | Five minutes will do it. Ready? |
| `v2.notifications.review_of_the_day` | revisão do dia | review of the day |
| `v2.notifications.your_review_is_due` | Sua revisão chegou | Your review is due |
| `v2.notifications.12_questions_are_back_so_you_don_t_forge` | 12 questões voltaram pra você não esquecer. | 12 questions are back so you don't forget. |
| `v2.notifications.freeze_used` | congelamento usado | freeze used |
| `v2.notifications.a_freeze_saved_your_streak` | Um congelamento salvou sua sequência | A freeze saved your streak |
| `v2.notifications.yesterday_was_a_blank_but_your_7_days_ca` | Ontem passou em branco, mas seus 7 dias continuam. | Yesterday was a blank, but your 7 days carry on. |

### v2.email-weekly · Weekly progress email

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.email-weekly.subject_line` | assunto | subject line |
| `v2.email-weekly.your_week_on_caramelcase_84_questions_an` | Sua semana no caramelCase: 84 questões e 7 dias seguidos | Your week on caramelCase: 84 questions and a 7-day streak |
| `v2.email-weekly.week_of_9_to_15_november` | semana de 9 a 15 de novembro | week of 9 to 15 November |
| `v2.email-weekly.your_week_carol` | Sua semana, Carol | Your week, Carol |
| `v2.email-weekly.questions` | questões | questions |
| `v2.email-weekly.accuracy` | acertos | accuracy |
| `v2.email-weekly.to_review_this_week` | Pra revisar esta semana | To review this week |
| `v2.email-weekly.recursion_and_binary_search_had_the_most` | Recursão e busca binária foram os tópicos com mais erros. Uma sessão de cada resolve. | Recursion and binary search had the most misses. One session of each will sort it out. |
| `v2.email-weekly.you_get_this_summary_every_monday` | Você recebe este resumo toda segunda. | You get this summary every Monday. |
| `v2.email-weekly.unsubscribe_from_these_emails` | Cancelar estes e-mails | Unsubscribe from these emails |
| `v2.email-weekly.notification_settings` | Ajustar notificações | Notification settings |

### v2.shell-splash · Splash screen

Uses common strings only.

### v2.admin-1-list · Admin · question list

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.admin-1-list.admin` | admin | admin |
| `v2.admin-1-list.question_review_internal_use` | revisão de questões · uso interno | question review · internal use |
| `v2.admin-1-list.7_of_1_284` | 7 de 1.284 | 7 of 1,284 |
| `v2.admin-1-list.all` | Todas | All |
| `v2.admin-1-list.with_reports` | Com reports | With reports |
| `v2.admin-1-list.in_review` | Em revisão | In review |
| `v2.admin-1-list.retired` | Aposentadas | Retired |
| `v2.admin-1-list.search_by_id_or_text` | Buscar por id ou texto | Search by id or text |
| `v2.admin-1-list.id` | id | id |
| `v2.admin-1-list.question` | enunciado | question |
| `v2.admin-1-list.accuracy` | acerto | accuracy |
| `v2.admin-1-list.answers` | respostas | answers |
| `v2.admin-1-list.reports` | reports | reports |
| `v2.admin-1-list.status` | status | status |
| `v2.admin-1-list.data_structures_stacks_and_queues` | Estruturas de Dados · Pilhas e filas | Data Structures · Stacks and queues |
| `v2.admin-1-list.approved` | Aprovada | Approved |
| `v2.admin-1-list.algorithms_binary_search` | Algoritmos · Busca binária | Algorithms · Binary search |
| `v2.admin-1-list.programming_recursion` | Programação · Recursão | Programming · Recursion |
| `v2.admin-1-list.in_a_system_with_demand_paging_what_happ` | Em um sistema com paginação por demanda, o que acontece quando um processo acessa uma página que não está na memória principal? | In a system with demand paging, what happens when a process accesses a page that is not in main memory? |
| `v2.admin-1-list.operating_systems_memory` | Sistemas Operacionais · Memória | Operating Systems · Memory |
| `v2.admin-1-list.put_the_steps_of_binary_search_in_order` | Coloque os passos da busca binária em ordem. | Put the steps of binary search in order. |
| `v2.admin-1-list.complete_the_recursive_function_that_com` | Complete a função recursiva que calcula o fatorial. | Complete the recursive function that computes the factorial. |
| `v2.admin-1-list.in_a_queue_the_first_element_in_is_the_f` | Em uma fila, o primeiro elemento a entrar é o primeiro a sair. | In a queue, the first element in is the first one out. |
| `v2.admin-1-list.retired_2` | Aposentada | Retired |

### v2.admin-2-edit · Admin · edit, approve, retire

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.admin-2-edit.admin` | admin | admin |
| `v2.admin-2-edit.question_review_internal_use` | revisão de questões · uso interno | question review · internal use |
| `v2.admin-2-edit.7_of_1_284` | 7 de 1.284 | 7 of 1,284 |
| `v2.admin-2-edit.all` | Todas | All |
| `v2.admin-2-edit.with_reports` | Com reports | With reports |
| `v2.admin-2-edit.in_review` | Em revisão | In review |
| `v2.admin-2-edit.retired` | Aposentadas | Retired |
| `v2.admin-2-edit.search_by_id_or_text` | Buscar por id ou texto | Search by id or text |
| `v2.admin-2-edit.id` | id | id |
| `v2.admin-2-edit.question` | enunciado | question |
| `v2.admin-2-edit.accuracy` | acerto | accuracy |
| `v2.admin-2-edit.answers` | respostas | answers |
| `v2.admin-2-edit.reports` | reports | reports |
| `v2.admin-2-edit.status` | status | status |
| `v2.admin-2-edit.data_structures_stacks_and_queues` | Estruturas de Dados · Pilhas e filas | Data Structures · Stacks and queues |
| `v2.admin-2-edit.approved` | Aprovada | Approved |
| `v2.admin-2-edit.algorithms_binary_search` | Algoritmos · Busca binária | Algorithms · Binary search |
| `v2.admin-2-edit.programming_recursion` | Programação · Recursão | Programming · Recursion |
| `v2.admin-2-edit.in_a_system_with_demand_paging_what_happ` | Em um sistema com paginação por demanda, o que acontece quando um processo acessa uma página que não está na memória principal? | In a system with demand paging, what happens when a process accesses a page that is not in main memory? |
| `v2.admin-2-edit.operating_systems_memory` | Sistemas Operacionais · Memória | Operating Systems · Memory |
| `v2.admin-2-edit.put_the_steps_of_binary_search_in_order` | Coloque os passos da busca binária em ordem. | Put the steps of binary search in order. |
| `v2.admin-2-edit.complete_the_recursive_function_that_com` | Complete a função recursiva que calcula o fatorial. | Complete the recursive function that computes the factorial. |
| `v2.admin-2-edit.in_a_queue_the_first_element_in_is_the_f` | Em uma fila, o primeiro elemento a entrar é o primeiro a sair. | In a queue, the first element in is the first one out. |
| `v2.admin-2-edit.retired_2` | Aposentada | Retired |
| `v2.admin-2-edit.close_panel` | Fechar painel | Close panel |
| `v2.admin-2-edit.question_text` | Enunciado | Question text |
| `v2.admin-2-edit.correct` | correta | correct |
| `v2.admin-2-edit.reports_3` | Reports · 3 | Reports · 3 |
| `v2.admin-2-edit.ambiguous_wording` | Enunciado ambíguo | Ambiguous wording |
| `v2.admin-2-edit.wrong_answer` | Resposta errada | Wrong answer |
| `v2.admin-2-edit.is_the_array_in_ascending_order_it_isn_t` | “O vetor está em ordem crescente? Não fica claro.” | “Is the array in ascending order? It isn't clear.” |
| `v2.admin-2-edit.save_changes` | Salvar edição | Save changes |
| `v2.admin-2-edit.approve` | Aprovar | Approve |
| `v2.admin-2-edit.retire` | Aposentar | Retire |

### v2.store-1 · Store screenshot 1 · Google Play 1080 × 1920 at 1/3

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.store-1.computer_science_in_five_minutes` | Ciência da computação em cinco minutos | Computer science in five minutes |

### v2.store-2 · Store screenshot 2 · Google Play 1080 × 1920 at 1/3

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.store-2.understand_the_why_behind_every_answer` | Entenda o porquê de cada resposta | Understand the why behind every answer |
| `v2.store-2.correct` | Correta | Correct |

### v2.store-3 · Store screenshot 3 · Google Play 1080 × 1920 at 1/3

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.store-3.your_rating_climbs_with_you` | Seu rating sobe com você | Your rating climbs with you |

### v2.store-4 · Store screenshot 4 · Google Play 1080 × 1920 at 1/3

| Key | PT-BR | EN |
| --- | --- | --- |
| `v2.store-4.keep_your_streak_going` | Mantenha a sequência | Keep your streak going |

## V3

### v3.pricing · Pricing · monthly

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.pricing.plans` | Planos | Plans |
| `v3.pricing.free` | Grátis | Free |
| `v3.pricing.with_a_daily_limit_and_ads` | Com limite diário e anúncios. | With a daily limit and ads. |
| `v3.pricing.plan_benefit` | [Benefício do plano] | [Plan benefit] |
| `v3.pricing.current_plan` | Plano atual | Current plan |
| `v3.pricing.plus` | Plus | Plus |
| `v3.pricing.billed_monthly` | cobrado todo mês | billed monthly |
| `v3.pricing.subscribe_to_plus` | Assinar Plus | Subscribe to Plus |
| `v3.pricing.pro` | Pro | Pro |
| `v3.pricing.subscribe_to_pro` | Assinar Pro | Subscribe to Pro |
| `v3.pricing.max` | Max | Max |
| `v3.pricing.subscribe_to_max` | Assinar Max | Subscribe to Max |
| `v3.pricing.the_price_you_see_is_the_price_you_pay_c` | O preço na tela é o preço cobrado. Cancele quando quiser, em dois toques, em Ajustes. | The price you see is the price you pay. Cancel any time, in two taps, in Settings. |

### v3.paywall-1-limit · Paywall · daily limit reached

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.paywall-1-limit.that_s_all_for_today` | Acabaram as questões de hoje | That's all for today |
| `v3.paywall-1-limit.back_in_5_h_12_min` | Voltam em 5 h 12 min | Back in 5 h 12 min |
| `v3.paywall-1-limit.you_can_still` | Ainda dá pra | You can still |
| `v3.paywall-1-limit.do_today_s_review` | Fazer sua revisão de hoje | Do today's review |
| `v3.paywall-1-limit.see_your_profile_and_progress` | Ver seu perfil e seu progresso | See your profile and progress |
| `v3.paywall-1-limit.want_to_keep_going_now` | Quer continuar agora? | Want to keep going now? |
| `v3.paywall-1-limit.plans_from_r_15_a_month_with_no_daily_li` | Planos a partir de R$ 15 por mês, sem limite diário. | Plans from R$ 15 a month, with no daily limit. |

### v3.checkout-card · Checkout · card

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.checkout-card.subscribe_to_pro` | Assinar o Pro | Subscribe to Pro |
| `v3.checkout-card.renews_every_month_cancel_any_time_in_se` | Renova todo mês. Cancele quando quiser em Ajustes. | Renews every month. Cancel any time in Settings. |
| `v3.checkout-card.payment_method` | Forma de pagamento | Payment method |
| `v3.checkout-card.card` | Cartão | Card |
| `v3.checkout-card.pix` | Pix | Pix |
| `v3.checkout-card.card_number` | Número do cartão | Card number |
| `v3.checkout-card.expiry` | Validade | Expiry |
| `v3.checkout-card.mm_yy` | MM/AA | MM/YY |
| `v3.checkout-card.cvv` | CVV | CVV |
| `v3.checkout-card.name_on_card` | Nome no cartão | Name on card |
| `v3.checkout-card.as_it_appears_on_the_card` | Como está no cartão | As it appears on the card |
| `v3.checkout-card.subscribe_for_r_40_a_month` | Assinar por R$ 40 por mês | Subscribe for R$ 40 a month |

### v3.checkout-pix · Checkout · Pix

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.checkout-pix.subscribe_to_pro` | Assinar o Pro | Subscribe to Pro |
| `v3.checkout-pix.renews_every_month_cancel_any_time_in_se` | Renova todo mês. Cancele quando quiser em Ajustes. | Renews every month. Cancel any time in Settings. |
| `v3.checkout-pix.payment_method` | Forma de pagamento | Payment method |
| `v3.checkout-pix.card` | Cartão | Card |
| `v3.checkout-pix.pix` | Pix | Pix |
| `v3.checkout-pix.pix_qr_code` | QR code do Pix | Pix QR code |
| `v3.checkout-pix.scan_with_your_bank_s_app_or_copy_the_co` | Escaneie com o app do seu banco ou copie o código. | Scan with your bank's app or copy the code. |
| `v3.checkout-pix.00020126580014br_gov_bcb_pix0136` | 00020126580014br.gov.bcb.pix0136… | 00020126580014br.gov.bcb.pix0136… |
| `v3.checkout-pix.expires_in_14_52` | expira em 14:52 | expires in 14:52 |
| `v3.checkout-pix.copy_pix_code` | Copiar código Pix | Copy Pix code |
| `v3.checkout-pix.waiting_for_payment_confirmation_arrives` | Esperando o pagamento. A confirmação chega sozinha. | Waiting for payment. Confirmation arrives on its own. |

### v3.account-manage · Manage subscription

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.account-manage.subscription` | Assinatura | Subscription |
| `v3.account-manage.active` | Ativo | Active |
| `v3.account-manage.next_charge` | Próxima cobrança | Next charge |
| `v3.account-manage.16_december_2026` | 16 de dezembro de 2026 | 16 December 2026 |
| `v3.account-manage.payment` | Pagamento | Payment |
| `v3.account-manage.card_ending_4417` | Cartão final 4417 | Card ending 4417 |
| `v3.account-manage.change_plan` | Trocar de plano | Change plan |
| `v3.account-manage.cancel_subscription` | Cancelar assinatura | Cancel subscription |
| `v3.account-manage.cancelling_takes_two_taps_you_keep_pro_u` | Cancelar leva dois toques. Você mantém o Pro até o fim do período já pago. | Cancelling takes two taps. You keep Pro until the end of the period you've paid for. |

### v3.tutor-chat · AI tutor chat

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.tutor-chat.mel_tutor` | Mel · tutor | Mel · tutor |
| `v3.tutor-chat.about_recursion` | sobre: recursão | about: recursion |
| `v3.tutor-chat.tutor_messages` | Mensagens com o tutor | Tutor messages |
| `v3.tutor-chat.12_of_20` | 12 de 20 | 12 of 20 |
| `v3.tutor-chat.messages_used` | Mensagens usadas | Messages used |
| `v3.tutor-chat.why_was_i_wrong` | Por que eu errei? | Why was I wrong? |
| `v3.tutor-chat.you_picked_16_but_f_multiplies_n_by_f_n` | Você marcou 16, mas f multiplica n por f(n - 1) até chegar em 1: | You picked 16, but f multiplies n by f(n - 1) until it reaches 1: |
| `v3.tutor-chat.the_result_is_24` | O resultado é 24. | The result is 24. |
| `v3.tutor-chat.what_about_f_5` | E se fosse f(5)? | What about f(5)? |
| `v3.tutor-chat.mel_thinking` | Mel pensando | Mel thinking |
| `v3.tutor-chat.mel_is_typing` | Mel está digitando | Mel is typing |
| `v3.tutor-chat.show_another_example` | Mostra outro exemplo | Show another example |
| `v3.tutor-chat.explain_more_slowly` | Explica mais devagar | Explain more slowly |
| `v3.tutor-chat.message_to_the_tutor` | Mensagem para o tutor | Message to the tutor |
| `v3.tutor-chat.ask_mel` | Pergunte ao Mel | Ask Mel |
| `v3.tutor-chat.the_question` | a questão | the question |

### v3.tracks · Exam track home

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.tracks.exam_track` | Trilha de prova | Exam track |
| `v3.tracks.exam_name_2_january_2027` | [nome da prova] · 2 de janeiro de 2027 | [exam name] · 2 January 2027 |
| `v3.tracks.days_until_the_exam` | dias até a prova | days until the exam |
| `v3.tracks.at_your_pace_you_can_finish_3_more_mock` | No seu ritmo, dá pra fechar mais 3 simulados até lá. | At your pace, you can finish 3 more mock exams before then. |
| `v3.tracks.full_mock_exams` | Simulados completos | Full mock exams |
| `v3.tracks.mock_exam_1` | Simulado 1 | Mock exam 1 |
| `v3.tracks.70_questions_4_h` | 70 questões · 4 h | 70 questions · 4 h |
| `v3.tracks.mock_exam_2` | Simulado 2 | Mock exam 2 |
| `v3.tracks.mock_exam_3` | Simulado 3 | Mock exam 3 |
| `v3.tracks.readiness_by_subject` | Preparo por matéria | Readiness by subject |
| `v3.tracks.candidate_ranking` | Ranking de candidatos | Candidate ranking |
| `v3.tracks.you_re_128th_of_1_940` | Você está em 128º de 1.940. | You're 128th of 1,940. |
| `v3.tracks.ana_l` | Ana L. | Ana L. |
| `v3.tracks.rafael_m` | Rafael M. | Rafael M. |
| `v3.tracks.carol_n` | Carol N. | Carol N. |
| `v3.tracks.you` | Você | You |

### v3.writecode · Write-code question

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.writecode.arrays` | Vetores | Arrays |
| `v3.writecode.write_the_code` | escreva o código | write the code |
| `v3.writecode.write_a_function_that_returns_the_larges` | Escreva uma função que devolve o maior elemento de um vetor não vazio. | Write a function that returns the largest element of a non-empty list. |
| `v3.writecode.tests` | Testes | Tests |
| `v3.writecode.2_of_3_passed` | 2 de 3 passaram | 2 of 3 passed |
| `v3.writecode.maior_3_9_2` | maior([3, 9, 2]) | maior([3, 9, 2]) |
| `v3.writecode.passed` | passou | passed |
| `v3.writecode.maior_7` | maior([7]) | maior([7]) |
| `v3.writecode.maior_3_1_7` | maior([-3, -1, -7]) | maior([-3, -1, -7]) |
| `v3.writecode.failed` | falhou | failed |
| `v3.writecode.expected_1_got_0` | esperado: -1 · veio: 0 | expected: -1 · got: 0 |
| `v3.writecode.hint_1_of_3` | Dica 1 de 3 | Hint 1 of 3 |
| `v3.writecode.next_hint` | Próxima dica | Next hint |
| `v3.writecode.what_if_every_number_is_negative_what_va` | E se todos os números forem negativos? Com que valor m deveria começar? | What if every number is negative? What value should m start with? |
| `v3.writecode.run` | Executar | Run |
| `v3.writecode.ctrl` | Ctrl | Ctrl |
| `v3.writecode.runs` | executa | runs |

### v3.referral · Referral

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.referral.refer_and_earn` | Indique e ganhe | Refer and earn |
| `v3.referral.invite_a_classmate` | Chame um colega | Invite a classmate |
| `v3.referral.when_they_finish_their_first_session_you` | Quando ele terminar a primeira sessão, vocês dois ganham [RECOMPENSA]. | When they finish their first session, you both get [REWARD]. |
| `v3.referral.your_link` | Seu link | Your link |
| `v3.referral.your_domain_c_carol7` | [seu-dominio]/c/CAROL7 | [your-domain]/c/CAROL7 |
| `v3.referral.copy` | Copiar | Copy |
| `v3.referral.share` | Compartilhar | Share |
| `v3.referral.your_invites` | Seus convites | Your invites |
| `v3.referral.1_of_2_complete` | 1 de 2 concluído | 1 of 2 complete |
| `v3.referral.rafael_m` | Rafael M. | Rafael M. |
| `v3.referral.reward_unlocked` | Recompensa liberada | Reward unlocked |
| `v3.referral.bia_s` | Bia S. | Bia S. |
| `v3.referral.first_session_pending` | Falta a 1ª sessão | First session pending |

### v3.pricing-annual · Pricing · annual

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.pricing-annual.plans` | Planos | Plans |
| `v3.pricing-annual.free` | Grátis | Free |
| `v3.pricing-annual.year` | /ano | /year |
| `v3.pricing-annual.with_a_daily_limit_and_ads` | Com limite diário e anúncios. | With a daily limit and ads. |
| `v3.pricing-annual.plan_benefit` | [Benefício do plano] | [Plan benefit] |
| `v3.pricing-annual.current_plan` | Plano atual | Current plan |
| `v3.pricing-annual.plus` | Plus | Plus |
| `v3.pricing-annual.yearly` | [ANUAL] | [YEARLY] |
| `v3.pricing-annual.billed_once_a_year` | cobrado uma vez por ano | billed once a year |
| `v3.pricing-annual.subscribe_to_plus` | Assinar Plus | Subscribe to Plus |
| `v3.pricing-annual.pro` | Pro | Pro |
| `v3.pricing-annual.subscribe_to_pro` | Assinar Pro | Subscribe to Pro |
| `v3.pricing-annual.max` | Max | Max |
| `v3.pricing-annual.subscribe_to_max` | Assinar Max | Subscribe to Max |
| `v3.pricing-annual.the_price_you_see_is_the_price_you_pay_c` | O preço na tela é o preço cobrado. Cancele quando quiser, em dois toques, em Ajustes. | The price you see is the price you pay. Cancel any time, in two taps, in Settings. |

### v3.paywall-2-locked · Paywall · locked feature tapped

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.paywall-2-locked.exam_mode_is_part_of_the_paid_plans` | Modo prova é dos planos pagos | Exam mode is part of the paid plans |
| `v3.paywall-2-locked.timed_mock_exams_with_a_report_by_topic` | Simulados cronometrados com relatório por tópico. Planos a partir de R$ 15 por mês. | Timed mock exams with a report by topic. Plans from R$ 15 a month. |
| `v3.paywall-2-locked.not_now` | Agora não | Not now |

### v3.paywall-3-upsell · Paywall · end-of-session upsell

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.paywall-3-upsell.enjoyed_the_session` | Curtiu a sessão? | Enjoyed the session? |
| `v3.paywall-3-upsell.practice_with_no_daily_limit_plans_from` | Pratique sem limite diário. Planos a partir de R$ 15 por mês. | Practice with no daily limit. Plans from R$ 15 a month. |
| `v3.paywall-3-upsell.dismiss` | Dispensar | Dismiss |

### v3.checkout-success · Checkout · success

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.checkout-success.subscription_active` | Assinatura ativa | Subscription active |
| `v3.checkout-success.you_re_on_pro_your_next_charge_is_on_16` | Você está no Pro. A próxima cobrança é em 16 de dezembro de 2026. | You're on Pro. Your next charge is on 16 December 2026. |
| `v3.checkout-success.see_my_subscription` | Ver minha assinatura | See my subscription |

### v3.checkout-failure · Checkout · payment failed

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.checkout-failure.the_payment_didn_t_go_through` | O pagamento não passou | The payment didn't go through |
| `v3.checkout-failure.nothing_was_charged_check_your_card_deta` | Nada foi cobrado. Confira os dados do cartão ou tente outro jeito de pagar. | Nothing was charged. Check your card details or try another way to pay. |
| `v3.checkout-failure.try_again` | Tentar de novo | Try again |
| `v3.checkout-failure.pay_with_pix` | Pagar com Pix | Pay with Pix |

### v3.account-cancel · Cancel subscription · confirm

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.account-cancel.subscription` | Assinatura | Subscription |
| `v3.account-cancel.active` | Ativo | Active |
| `v3.account-cancel.next_charge` | Próxima cobrança | Next charge |
| `v3.account-cancel.16_december_2026` | 16 de dezembro de 2026 | 16 December 2026 |
| `v3.account-cancel.payment` | Pagamento | Payment |
| `v3.account-cancel.card_ending_4417` | Cartão final 4417 | Card ending 4417 |
| `v3.account-cancel.change_plan` | Trocar de plano | Change plan |
| `v3.account-cancel.cancel_subscription` | Cancelar assinatura | Cancel subscription |
| `v3.account-cancel.cancelling_takes_two_taps_you_keep_pro_u` | Cancelar leva dois toques. Você mantém o Pro até o fim do período já pago. | Cancelling takes two taps. You keep Pro until the end of the period you've paid for. |
| `v3.account-cancel.cancel_pro` | Cancelar o Pro? | Cancel Pro? |
| `v3.account-cancel.you_stay_on_pro_until_16_december_2026_a` | Você continua no Pro até 16 de dezembro de 2026. Depois volta pro plano grátis e mantém todo o seu progresso. | You stay on Pro until 16 December 2026. After that you return to the free plan and keep all your progress. |
| `v3.account-cancel.keep_pro` | Manter o Pro | Keep Pro |

### v3.adoffer-life · Opt-in ad · restore a life

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.adoffer-life.0_of_3_lives` | 0 de 3 vidas | 0 of 3 lives |
| `v3.adoffer-life.out_of_lives` | Acabaram as vidas | Out of lives |
| `v3.adoffer-life.next_life_in_24_10` | Próxima vida em 24:10 | Next life in 24:10 |
| `v3.adoffer-life.how_lives_come_back` | Como as vidas voltam | How lives come back |
| `v3.adoffer-life.one_life_every_30_minutes` | Uma vida a cada 30 minutos | One life every 30 minutes |
| `v3.adoffer-life.they_refill_on_their_own_up_to_3` | Elas voltam sozinhas, até o máximo de 3. | They refill on their own, up to 3. |
| `v3.adoffer-life.review_doesn_t_cost_lives` | Revisão não gasta vidas | Review doesn't cost lives |
| `v3.adoffer-life.you_can_do_your_reviews_while_you_wait` | Dá pra praticar suas revisões enquanto espera. | You can do your reviews while you wait. |
| `v3.adoffer-life.do_a_review` | Fazer revisão | Do a review |
| `v3.adoffer-life.1_of_3_lives` | 1 de 3 vidas | 1 of 3 lives |
| `v3.adoffer-life.restore_a_life_now` | Recuperar uma vida agora? | Restore a life now? |
| `v3.adoffer-life.watch_a_short_ad_and_get_a_life_or_wait` | Assista a um anúncio curto e ganhe uma vida. Ou espere: a próxima volta em 24:10. | Watch a short ad and get a life. Or wait: the next one is back in 24:10. |
| `v3.adoffer-life.watch_ad` | Assistir anúncio | Watch ad |
| `v3.adoffer-life.no_thanks` | Não, obrigado | No thanks |

### v3.tutor-entry-1-wrong · Tutor entry · from a wrong answer

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.tutor-entry-1-wrong.in_a_stack_the_last_element_inserted_is` | Na pilha, o último elemento inserido é o primeiro a sair, como uma pilha de pratos. A fila faz o contrário: é FIFO. | In a stack, the last element inserted is the first one out, like a stack of plates. A queue does the opposite: it's FIFO. |
| `v3.tutor-entry-1-wrong.why_was_i_wrong` | Por que eu errei? | Why was I wrong? |

### v3.tutor-entry-2-topic · Tutor entry · from a topic

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.tutor-entry-2-topic.data_structures` | estruturas de dados | data structures |
| `v3.tutor-entry-2-topic.mastery` | Domínio | Mastery |
| `v3.tutor-entry-2-topic.practice` | Praticar | Practice |
| `v3.tutor-entry-2-topic.ask_mel` | Perguntar ao Mel | Ask Mel |

### v3.tutor-out · Tutor · message allowance used up

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.tutor-out.mel_tutor` | Mel · tutor | Mel · tutor |
| `v3.tutor-out.about_recursion` | sobre: recursão | about: recursion |
| `v3.tutor-out.tutor_messages` | Mensagens com o tutor | Tutor messages |
| `v3.tutor-out.20_of_20` | 20 de 20 | 20 of 20 |
| `v3.tutor-out.messages_used` | Mensagens usadas | Messages used |
| `v3.tutor-out.that_s_all_for_today_they_re_back_tomorr` | Acabaram por hoje. Voltam amanhã. | That's all for today. They're back tomorrow. |
| `v3.tutor-out.why_was_i_wrong` | Por que eu errei? | Why was I wrong? |
| `v3.tutor-out.you_picked_16_but_f_multiplies_n_by_f_n` | Você marcou 16, mas f multiplica n por f(n - 1) até chegar em 1: | You picked 16, but f multiplies n by f(n - 1) until it reaches 1: |
| `v3.tutor-out.the_result_is_24` | O resultado é 24. | The result is 24. |
| `v3.tutor-out.you_re_out_of_messages_for_today` | Acabaram as mensagens de hoje | You're out of messages for today |
| `v3.tutor-out.they_re_back_tomorrow_your_conversations` | Elas voltam amanhã. Suas conversas ficam salvas. | They're back tomorrow. Your conversations are saved. |
| `v3.tutor-out.dismiss` | Dispensar | Dismiss |
| `v3.tutor-out.message_to_the_tutor` | Mensagem para o tutor | Message to the tutor |
| `v3.tutor-out.no_messages_left_today` | Sem mensagens por hoje | No messages left today |

### v3.beat-1-offer · Beat the ad · challenge offered

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.beat-1-offer.mel_looking_mischievous` | Mel com cara de travesso | Mel looking mischievous |
| `v3.beat-1-offer.break` | intervalo | break |
| `v3.beat-1-offer.get_it_right_skip_the_ad` | Acerte e pule o anúncio | Get it right, skip the ad |
| `v3.beat-1-offer.one_question_get_it_right_and_there_s_no` | Uma questão. Se acertar, não tem anúncio agora. | One question. Get it right and there's no ad now. |
| `v3.beat-1-offer.take_the_challenge` | Aceitar o desafio | Take the challenge |
| `v3.beat-1-offer.watch_the_ad` | Ver o anúncio | Watch the ad |

### v3.beat-2-question · Beat the ad · challenge question

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.beat-2-question.give_up_and_watch_the_ad` | Desistir e ver o anúncio | Give up and watch the ad |
| `v3.beat-2-question.ad_challenge` | desafio do anúncio | ad challenge |

### v3.beat-3-double · Beat the ad · win, double or nothing offered

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.beat-3-double.ad_skipped` | anúncio pulado | ad skipped |
| `v3.beat-3-double.the_next_break_is_already_further_away` | O próximo intervalo já ficou mais longe. | The next break is already further away. |
| `v3.beat-3-double.double_or_nothing` | Dobro ou nada? | Double or nothing? |
| `v3.beat-3-double.get_one_more_right_and_the_next_break_mo` | Acerte mais uma e o próximo intervalo fica bem mais longe. Se errar, o anúncio toca agora. | Get one more right and the next break moves much further away. Miss it and the ad plays now. |
| `v3.beat-3-double.double_or_nothing_2` | Dobro ou nada | Double or nothing |
| `v3.beat-3-double.i_m_good_continue` | Tô de boa, continuar | I'm good, continue |

### v3.beat-4-win · Beat the ad · double won

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.beat-4-win.doubled` | dobrou | doubled |
| `v3.beat-4-win.two_for_two` | Dois de dois! | Two for two! |
| `v3.beat-4-win.ad_skipped_and_the_next_break_is_much_fu` | Anúncio pulado, e o próximo intervalo ficou bem mais longe. | Ad skipped, and the next break is much further away. |
| `v3.beat-4-win.back_to_the_session` | Voltar pra sessão | Back to the session |

### v3.beat-5-lose · Beat the ad · lost

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.beat-5-lose.not_this_time` | não foi dessa vez | not this time |
| `v3.beat-5-lose.close` | Quase. | Close. |
| `v3.beat-5-lose.the_ad_plays_now_and_the_next_break_come` | O anúncio toca agora e o próximo intervalo vem um pouco antes. Na próxima você pula. | The ad plays now and the next break comes a little sooner. You'll skip the next one. |
| `v3.beat-5-lose.watch_the_ad` | Ver o anúncio | Watch the ad |

### v3.beat-6-adbreak · Beat the ad · ad break frame

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.beat-6-adbreak.ad` | Anúncio | Ad |
| `v3.beat-6-adbreak.continues_in_5_s` | Continua em 5 s | Continues in 5 s |
| `v3.beat-6-adbreak.ad_slot_fixed_size` | espaço do anúncio · tamanho fixo | ad slot · fixed size |
| `v3.beat-6-adbreak.your_session_is_saved_and_resumes_right` | Sua sessão está salva e volta logo depois. | Your session is saved and resumes right after. |
| `v3.beat-6-adbreak.back_to_the_session` | Voltar pra sessão | Back to the session |

### v3.repair-1-free · Streak repair · offer on the free plan

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.repair-1-free.your_7_day_streak_ended` | Sua sequência de 7 dias terminou | Your 7-day streak ended |
| `v3.repair-1-free.watch_a_short_ad_and_your_7_days_come_ba` | Assista a um anúncio curto e seus 7 dias voltam. | Watch a short ad and your 7 days come back. |
| `v3.repair-1-free.you_can_restore_it_for_another_41_12_08` | Dá pra recuperar por mais 41:12:08 | You can restore it for another 41:12:08 |
| `v3.repair-1-free.watch_ad_and_restore` | Assistir anúncio e recuperar | Watch ad and restore |
| `v3.repair-1-free.no_thanks` | Não, obrigado | No thanks |

### v3.repair-2-paid · Streak repair · offer on a paid plan

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.repair-2-paid.your_7_day_streak_ended` | Sua sequência de 7 dias terminou | Your 7-day streak ended |
| `v3.repair-2-paid.on_your_plan_restoring_takes_one_tap_no` | No seu plano, recuperar é um toque. Sem anúncio. | On your plan, restoring takes one tap. No ad. |
| `v3.repair-2-paid.pro` | PRO | PRO |
| `v3.repair-2-paid.you_can_restore_it_for_another_41_12_08` | Dá pra recuperar por mais 41:12:08 | You can restore it for another 41:12:08 |
| `v3.repair-2-paid.restore_streak` | Recuperar sequência | Restore streak |
| `v3.repair-2-paid.no_thanks` | Não, obrigado | No thanks |

### v3.repair-3-restored · Streak repair · restored

| Key | PT-BR | EN |
| --- | --- | --- |
| `v3.repair-3-restored.streak_restored` | Sequência recuperada | Streak restored |
| `v3.repair-3-restored.your_7_days_are_back_practice_today_to_k` | Seus 7 dias estão de volta. Pratique hoje pra continuar. | Your 7 days are back. Practice today to keep going. |
