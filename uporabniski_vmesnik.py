import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
import customtkinter as ctk
from math import gamma
import matplotlib.animation as animation



ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

# MODEL

def strosek_na_casovno_enoto(starost, strosek_popravila, m0, d, h):
    casi_do_naslednjih_okvar = sum(m0 * (d ** (starost + j)) for j in range(h)) #izračunamo čas do naslednjih okvar, z degradacijo
    return (h * strosek_popravila) / casi_do_naslednjih_okvar #vrnemo povprečen strošek na časovno enoto

def optimalno_st_popravil(strosek_zamenjave, strosek_popravila, m0, d, k_max=30):
    k_s = np.arange(1, k_max + 1) 
    g_vrednost = (strosek_zamenjave + k_s * strosek_popravila) / (m0 * (1 - d**k_s) / (1 - d)) #vrednosti funkcije g (strošek na časovno enoto)
    return int(k_s[np.argmin(g_vrednost)]), g_vrednost, k_s #dobimo ven vrednosti funkcije g in kje je dosežen minimum

def simuliraj_en_cikel(cas_zamenjava, strosek_zamenjave, strosek_popravila, m0, d, i0=0):
    cas = 0.0 
    strosek = 0.0
    starost = i0

    while starost < cas_zamenjava:
        cas_do_naslednje_okvare = m0 * (d ** starost) 
        t = np.random.exponential(cas_do_naslednje_okvare)
        cas += t
        strosek += strosek_popravila
        starost += 1

    strosek += strosek_zamenjave
    return strosek, cas #dobimo ven strošek in čas ki poteče do časa zamenjavne stroje

def narisi_g(strosek_zamenjave, strosek_popravila, m0, d):
    k_s = np.arange(1, 31)
    g_vrednosti = (strosek_zamenjave + k_s * strosek_popravila) / (m0 * (1 - d**k_s) / (1 - d))

    optimalno_st_popravil = k_s[np.argmin(g_vrednosti)]

    plt.figure(figsize=(6,4))
    plt.plot(k_s, g_vrednosti, marker="o", label="g(k)")
    plt.axvline(optimalno_st_popravil, linestyle="--", label=f"k* = {optimalno_st_popravil}")
    plt.xlabel("Število popravil k")
    plt.ylabel("Strošek na časovno enoto")
    plt.title("Funkcija stroškov na časovno enoto g(k)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return optimalno_st_popravil

def monte_carlo_strosek(cas_zamenjave, strosek_zamenjave, strosek_popravila, m0, d, N=5000, i0=0):
    stroski_na_casovno_enoto = []
    for _ in range(N):
        strosek, cas = simuliraj_en_cikel(cas_zamenjave, strosek_zamenjave, strosek_popravila, m0, d, i0)
        stroski_na_casovno_enoto.append(strosek / cas)
    return np.array(stroski_na_casovno_enoto) #ven dobimo celotno informacijo o naših simuliranih vrednostih (povprečje,varianco,...)


def graf_monte_carlo_primerjava(strosek_zamenjave, strosek_samo_popravilo, strosek_izpad, d, i0=0):
    m0 = slider_mu.get()
    strosek_popravilo = strosek_samo_popravilo + strosek_izpad

    k_s = np.arange(1, 31)
    g_vrednosti = (strosek_zamenjave + k_s * strosek_popravilo) / (m0 * (1 - d**k_s) / (1 - d))
    optimalno_st_popravil = int(k_s[np.argmin(g_vrednosti)])

    izbire = {
        f"Optimalna (k={optimalno_st_popravil})": optimalno_st_popravil,
        "k = 2": 2,
        "k = 5": 5,
        "k = 10": 10
    }#tukaj si izberemo kaj primerjamo pri številu popravil

    podatki = []
    oznake = []

    for oznaka, st_popavil in izbire.items():
        strosek = monte_carlo_strosek(st_popavil, strosek_zamenjave, strosek_popravilo, m0, d, N=5000, i0=i0)
        podatki.append(strosek)
        oznake.append(oznaka)

    plt.figure(figsize=(7,4))
    plt.boxplot(podatki, labels=oznake, showfliers=False)
    plt.ylabel("Strošek na časovno enoto")
    plt.title("Monte Carlo primerjava izbir števila zamenjav")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.show()

def nakljucen_cas_do_okvare(mu, porazdelitev, beta=1.0, sigma=0.5):
    if porazdelitev == "Eksponentna":
        return np.random.exponential(mu)
    elif porazdelitev == "Weibull":
        w = np.random.weibull(beta)
        return mu * w / gamma(1 + 1 / beta)
    elif porazdelitev == "Lognormalna":
        mu_l = np.log(mu) - 0.5 * sigma**2
        return np.random.lognormal(mu_l, sigma)


def graf_zivljenjske_poti():
    try:
        Cn = slider_Cn.get()
        Cp = slider_Cp.get()
        Cd = slider_Cd.get()
        d  = slider_d.get()
        i0 = slider_i0.get()
        m0 = slider_mu.get()

        strosek_popravila = Cp + Cd

        # parametri porazdelitev
        beta = slider_beta.get()
        sigma = slider_sigma.get()

        # optimalni threshold
        k_s = np.arange(1, 31)
        g_vrednosti = (Cn + k_s*strosek_popravila) / (m0 * (1 - d**k_s) / (1 - d))
        optimalno_st_popravil = int(k_s[np.argmin(g_vrednosti)])

        
        porazdelitve = ["Eksponentna", "Weibull", "Lognormalna"]
    
        plt.figure(figsize=(9,4))

        for dist in porazdelitve:
            cas = [0.0]
            stanje_degradacije = [d**i0]

            t = 0.0
            i = i0

            while i < optimalno_st_popravil:
                mu_i = m0 * (d ** i)
                dt = nakljucen_cas_do_okvare(mu_i, dist, beta, sigma)

                t += dt
                cas.append(t)
                stanje_degradacije.append(d**i)

                i += 1
                cas.append(t)
                stanje_degradacije.append(d**i)

            plt.step(
                cas,
                stanje_degradacije,
                where="post",
                linewidth=2,
                label=dist
                )

        plt.xlabel("Čas")
        plt.ylabel("Stanje / zanesljivost stroja")
        plt.title("Življenjske poti stroja – primerjava porazdelitev")
        plt.ylim(0, 1.05)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Napaka", str(e))


def monte_carlo_pot_zivljenjske_poti(m0, d, optimalno_st_popravil, i0, porazdelitev, N=5000, beta=1.0, sigma=0.5):
    st_popravil = optimalno_st_popravil - i0
    matrika_casov_med_stanji = np.zeros((N, st_popravil))

    for n in range(N):
        i = i0
        for j in range(st_popravil):
            mu_i = m0 * (d ** i)
            dt = nakljucen_cas_do_okvare(mu_i, porazdelitev, beta, sigma)
            matrika_casov_med_stanji[n, j] = dt
            i += 1

    povprecni_casi = matrika_casov_med_stanji.mean(axis=0) #povprečni čas prehoda za vsako stanje
    skupni_casi = np.concatenate([[0], np.cumsum(povprecni_casi)])
    stanje_stroja = np.array([d ** (i0 + j) for j in range(st_popravil + 1)])

    return skupni_casi, stanje_stroja


def graf_povprecne_zivljenjske_poti():
    try:
        Cn = slider_Cn.get()
        Cp = slider_Cp.get()
        Cd = slider_Cd.get()
        d  = slider_d.get()
        i0 = int(slider_i0.get())
        m0 = slider_mu.get()

        beta = slider_beta.get()
        sigma = slider_sigma.get()

        stroski_popravila = Cp + Cd

        k_s = np.arange(1, 31)
        g_vrednosti = (Cn + k_s*stroski_popravila) / (m0 * (1 - d**k_s) / (1 - d))
        optimalno_st_popravil = int(k_s[np.argmin(g_vrednosti)])

        plt.figure(figsize=(9,4))

        for porazdelitev in ["Eksponentna", "Weibull", "Lognormalna"]:
            povprecen_cas, stanje_stroja = monte_carlo_pot_zivljenjske_poti(m0, d, optimalno_st_popravil, i0, porazdelitev, N=1000, beta=beta, sigma=sigma)

            plt.step(
                povprecen_cas,
                stanje_stroja,
                where="post",
                linewidth=3,
                label=f"{porazdelitev} – povprečje"
            )

        plt.xlabel("Čas")
        plt.ylabel("Stanje / zanesljivost stroja")
        plt.title("Monte Carlo povprečne življenjske poti")
        plt.ylim(0, 1.05)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Napaka", str(e))


def animacija_funkcije_stroskov(stroski_zamenjave, stroski_samo_popravilio, stroski_izpad, m0):
    stroski_popravilo = stroski_samo_popravilio + stroski_izpad

    k_s = np.arange(1, 31)

    d_vrednosti = np.linspace(0.5, 0.95, 45)

    fig, ax = plt.subplots(figsize=(7,5))

    line, = ax.plot([], [], marker="o", lw=2) #prazen graf za g
    vline = ax.axvline(0, linestyle=":", color="gray") #navpična črta ki nam pokaze optimalni k
    text = ax.text(0.02, 0.95, "", transform=ax.transAxes) #besedilo na grafu

    ax.set_xlim(1, k_s[-1]) 
    ax.set_ylim(0, None) 
    ax.set_xlabel("Število popravil k")
    ax.set_ylabel("Strošek na časovno enoto g(k)")
    ax.set_title("Animacija grafa stroškov na časovno enoto glede na degradacijo d")
    ax.grid(True)

    def update(frame):
        d = d_vrednosti[frame] #vrednost degradacije za vsak frame
        g_vrednosti = (stroski_zamenjave + k_s * stroski_popravilo) / (m0 * (1 - d**k_s) / (1 - d))
        optimalno_st_popravil = k_s[np.argmin(g_vrednosti)]

        line.set_data(k_s, g_vrednosti) #narišemo novo krivuljo za trenutno vrednost d
        vline.set_xdata(optimalno_st_popravil) #premaknemo navpišno črto k nam pokaže kako se premika k*
        text.set_text(f"d = {d:.2f}   |   k* = {optimalno_st_popravil}") #na grafu napišemo nov d in k*

        ax.set_ylim(0, max(g_vrednosti)*1.1) #prilagodimo ylin
        return line, vline, text

    ani = animation.FuncAnimation( #ustvarimo animacijo
        fig,
        update,
        st_korakov=len(d_vrednosti),
        interval=120, #cas med sličicami
        blit=False #to pomeni da matplotlib nariše samo ti kar se spremeni
    )

    plt.show()


# CALLBACK: ODLOČITEV + GRAF

def izracun_optimalne_izbire():
    try:
        Cn = slider_Cn.get()
        Cp = slider_Cp.get()
        Cd = slider_Cd.get()
        d  = slider_d.get()
        i0 = slider_i0.get()
        m0 = slider_mu.get()

        C = Cp + Cd
        
        k_star, g_vals, _ = optimalno_st_popravil(Cn, C, m0, d)
        rZ = float(np.min(g_vals))

        remaining_repairs = max(k_star - i0, 0)

        # ODLOČITEV
        result_label.configure(
            text=
            "Optimalna izbira:\n\n"
            f"• Optimalno število popravil za nov stroj: k* = {k_star}\n"
            f"• Smiselno število popravil za naš stroj: {remaining_repairs}\n\n"
            f"→ {'ZAMENJAJ' if remaining_repairs == 0 else 'POPRAVI'}"
        )

        # GRAF
        
        i_vals = np.arange(0, 30)
        h = 1
        rR = np.array([strosek_na_casovno_enoto(i0 + i, C, m0, d, h=h) for i in i_vals])

        idx = np.where(rR >= rZ)[0]
        i_star = int(idx[0]) if len(idx) else None

        plt.figure(figsize=(6,4))
        plt.plot(i_vals, rR, marker="o", label="Strošek pri popravljanju")
        plt.axhline(rZ, linestyle="--", label="Stošek pri zamenjavi")

        if i_star is not None:
            plt.axvline(i_star, linestyle=":", label=f"Presečišče = {i_star}")

        plt.xlabel("Popravila od nakupa")
        plt.ylabel("Strošek na časovno enoto")
        plt.title("Graf optimalne odločitve")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Napaka", str(e))


def graf_heatmap():
    try:
        m0 = slider_mu.get()
        i0 = slider_i0.get()

        d_vrednosti = np.linspace(0.55, 0.95, 40)
        razmerje_cen = np.linspace(2, 15, 40) #strošek zamenjave gelde na strošek popravila in izpada dohodka
 
        H = np.zeros((len(razmerje_cen), len(d_vrednosti))) #naredimo začetno matriko ki bo vsebovala vrednosti k

        for i, razmerje in enumerate(razmerje_cen):
            for j, d in enumerate(d_vrednosti):
                C = 1.0 #nastavimo ker nas zanimajo samo razmerja in ne dejanske vrednosti
                Cn = razmerje * C
                optimalen_k, _, _ = optimalno_st_popravil(Cn, C, m0, d)

                if i0 == 0:
                    # nov stroj
                    H[i, j] = optimalen_k
                else:
                    # rabljen stroj
                    H[i, j] = max(optimalen_k - i0, 0)

        plt.figure(figsize=(8,6))
        plt.imshow(
            H,
            origin="lower",
            aspect="auto",
            extent=[d_vrednosti[0], d_vrednosti[-1], razmerje_cen[0], razmerje_cen[-1]] #pravilno označi osi
        )

        if i0 == 0:
            plt.colorbar(label="Optimalno število popravil k*")
            title = "Heatmap optimalnega števila popravil (nov stroj)"
        else:
            plt.colorbar(label="Število smiselnih popravil")
            title = f"Heatmap optimalnega števila popravil (rabljen stroj, i₀ = {i0})"

        plt.xlabel("Degradacija d")
        plt.ylabel("Razmerje stroškov Cn / (Cp + Cd)")
        plt.title(title)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Napaka", str(e))


# Dejanski izgled

root = ctk.CTk()
root.geometry("620x820")
root.title("Optimalno vzdrževanje – nov in rabljen stroj")


ctk.CTkLabel(
    root,
    text="Optimalno vzdrževanje",
    font=("Arial", 14)
).grid(row=0, column=0, columnspan=2, pady=10)



def make_slider(besedilo, zacetek, konec, vrstica, vmesni_korak):
    ctk.CTkLabel(root, text=besedilo).grid(
        row=vrstica, column=0, sticky="e", pady=4, padx=6
    )
    var = ctk.DoubleVar(value=zacetek) #naredimo drnik

    display = ctk.StringVar(value=f"{zacetek:.2f}") # da imamo samo 2 decimalki

    st_korakov = int(round((konec - zacetek) / vmesni_korak))

    slider = ctk.CTkSlider(
        root,
        from_=zacetek,
        to=konec,
        variable=var,
        number_of_steps=st_korakov
    )
    slider.grid(row=vrstica, column=1, sticky="ew", padx=10) #kje je slider

    ctk.CTkLabel( #tekst desno od drsnika
        root,
        textvariable=display, #da se samodejno prenavlja tekst
        width=80
    ).grid(row=vrstica, column=2, sticky="w")

    var.trace_add("write", lambda *_: display.set(f"{var.get():.2f}"))

    return slider


##############naredimo vse sliderje

slider_mu = make_slider("Pričakovana življenjska doba stroja", 1, 40, vrstica=1, vmesni_korak=0.25)
slider_mu.set(4)

slider_Cn = make_slider("Strošek novega stroja Cn", 2000, 15000, vrstica=2, vmesni_korak=1)
slider_Cn.set(8000)

slider_Cp = make_slider("Strošek popravila Cp", 100, 2000, vrstica=3, vmesni_korak=1)
slider_Cp.set(600)

slider_Cd = make_slider("Izguba dohodka Cd", 0, 2000, vrstica=4, vmesni_korak= 1)
slider_Cd.set(250)

slider_d = make_slider("Degradacija d", 0.50, 0.95, vrstica=5, vmesni_korak= 0.01)
slider_d.set(0.8)

slider_i0 = make_slider("Začetno stanje rabljenega stroja i₀", 0, 15, vrstica=6, vmesni_korak=1)
slider_i0.set(0)

slider_beta = make_slider("Weibull β", 0.1, 5.0, vrstica=14, vmesni_korak= 0.1)
slider_beta.set(1.0)

slider_sigma = make_slider("Lognormal σ", 0.1, 1.5, vrstica=15, vmesni_korak=0.1)
slider_sigma.set(0.5)



ctk.CTkButton(
    root,
    text="Optimalna izbira",
    command=izracun_optimalne_izbire,
).grid(row=7, column=0, columnspan=2, pady=6)


result_label = ctk.CTkLabel(
    root,
    text="",
    font=("Arial", 11),
    justify="left"
)
result_label.grid(row=8, column=0, columnspan=2, pady=10)

ctk.CTkButton(
    root,
    text="Prikaži heatmap",
    command=graf_heatmap
).grid(row=9, column=0, columnspan=2, pady=6)


ctk.CTkButton(
    root,
    text="Izriši funkcijo stroška na časovno enoto",
    command=lambda: narisi_g(
        slider_Cn.get(),
        slider_Cp.get() + slider_Cd.get(),
        slider_mu.get(),
        slider_d.get()
    )
).grid(row=10, column=0, columnspan=2, pady=6)

ctk.CTkButton(
    root,
    text="Monte Carlo validacija",
    command=lambda: graf_monte_carlo_primerjava(
        slider_Cn.get(),
        slider_Cp.get(),
        slider_Cd.get(),
        slider_d.get(),
        i0=int(slider_i0.get())
    )
).grid(row=11, column=0, columnspan=2, pady=6)


ctk.CTkButton(
    root,
    text="Primerjaj sample path (vse porazdelitve)",
    command=graf_zivljenjske_poti
).grid(row=16, column=0, columnspan=2, pady=6)

ctk.CTkButton(
    root,
    text="Monte Carlo povprečne življenjske poti",
    command=graf_povprecne_zivljenjske_poti
).grid(row=17, column=0, columnspan=2, pady=6)


ctk.CTkButton(
    root,
    text="Animacija g(k) vs degradacija",
    command=lambda: animacija_funkcije_stroskov(
        slider_Cn.get(),
        slider_Cp.get(),
        slider_Cd.get(),
        slider_mu.get()
    )
).grid(row=18, column=0, columnspan=2, pady=6)


root.mainloop()