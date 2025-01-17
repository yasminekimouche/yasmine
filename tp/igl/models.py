from django.db import models

from django.contrib.auth.models import AbstractUser


class PersonneAContacter(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)  

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('medecin', 'Médecin'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='Patient')

    def __str__(self):
        return self.username


 
class Etablissement(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nom} - {self.adresse}"

class Utilisateur(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)
    telephone = models.CharField(max_length=15)
    etablissement = models.ForeignKey(
        Etablissement,  # Relation un-à-plusieurs
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="utilisateurs"
    )

    def __str__(self):
        return self.username


class Patient(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_de_naissance = models.DateField("Date de naissance")
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)  
    nss = models.CharField(max_length=15, unique=True)  # Ajout de `unique` pour éviter les doublons
    mutuelle = models.CharField(max_length=100, blank=True, null=True)  # Optionnel
    personne_a_contacter = models.ForeignKey(
        'PersonneAContacter', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="patients"
    )  
    medecins = models.ManyToManyField(
        'Medecin', 
        blank=True,  # `null=True` n'est pas nécessaire pour ManyToManyField
        related_name="patients"
    )

    def __str__(self):
        return f"{self.nom} {self.prenom} (NSS : {self.nss})"

class Traitement(models.Model):
    nom = models.CharField(max_length=100)
    dose = models.CharField(max_length=100)  # Exemple : "500mg"
    consommation = models.CharField(
        max_length=100, 
        help_text="Par exemple : '3 comprimés'"
    )
    frequence = models.IntegerField(
        verbose_name="Fréquence (en jours)", 
        help_text="Par exemple : tous les 3 jours"
    )

    def __str__(self):
        return f"{self.nom} ({self.dose})"




class Ordonnance(models.Model):
    STATUT_CHOICES = [
        ('distribuee', 'Distribuée'),
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
    ]

    patient = models.ForeignKey(
        'Patient', 
        on_delete=models.CASCADE,  # Supprime l'ordonnance si le patient est supprimé
        related_name='ordonnances', 
        help_text="Patient associé à cette ordonnance"
    )
    date_emission = models.DateField("Date d'émission", auto_now_add=True)
    status = models.CharField(
        max_length=100, 
        choices=STATUT_CHOICES, 
        default='en_attente', 
        help_text="Statut actuel de l'ordonnance"
    )
    traitements = models.ManyToManyField(
        'Traitement', 
        related_name='ordonnances', 
        help_text="Liste des traitements inclus dans cette ordonnance"
    )

    def __str__(self):
        return f"Ordonnance du {self.date_emission} - {self.patient.nom} {self.patient.prenom}"





class DPI(models.Model):
    patient = models.OneToOneField(
        'Patient', 
        on_delete=models.CASCADE, 
        related_name='dossier_patient',  # Un nom inversé unique
        help_text="Le patient associé à ce DSI"
    )
    utilisateur = models.OneToOneField(
        'Utilisateur', 
        on_delete=models.CASCADE, 
        related_name='dossier_utilisateur',  # Un nom inversé unique
        help_text="L'utilisateur associé à ce DSI"
    )

    def __str__(self):
        return f"Dossier patient de {self.patient.nom} {self.patient.prenom}"






class Consultation(models.Model):
    date = models.DateField(
        "Date de consultation",
        auto_now_add=True,
        help_text="Date à laquelle la consultation a eu lieu"
    )
    resume = models.CharField(
        max_length=2500,
        help_text="Résumé de la consultation"
    )
    ordonnance = models.ForeignKey(
        'Ordonnance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations',
        help_text="Ordonnance liée à cette consultation (optionnelle)"
    )
    dpi = models.ForeignKey(
        DPI,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=None,
        related_name='consultations',
        help_text="DPI associé à cette consultation"
    )

    def __str__(self):
        return f"Consultation du {self.date}"



class Bilan(models.Model):
    prescription = models.CharField(
        max_length=255,
        help_text="Description de la prescription pour cet examen"
    )
    date_emission = models.DateField(
        "Date d'émission",
        auto_now_add=True
    )
    consultation = models.ForeignKey(
        'Consultation',
        on_delete=models.CASCADE,
        related_name='bilans',
        help_text="Consultation à laquelle ce bilan est associé"
    )

    def __str__(self):
        return f"Bilan : {self.prescription} pour la consultation du {self.consultation.date}"


class BilanBiologique(Bilan):
    resultat = models.TextField(
        help_text="Résultat du bilan biologique"
    )




class Medecin(models.Model):
    id = models.AutoField(primary_key=True)  # Définir un champ id explicite si nécessaire
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr {self.nom} {self.prenom} ({self.specialite})"

class test(models.Model):
    id = models.AutoField(primary_key=True)  # Définir un champ id explicite si nécessaire



class BilanRadiologique(Bilan):
    compte_rendu = models.TextField(
        help_text="Compte-rendu du bilan radiologique"
    )
    image_url = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Lien vers l'image radiologique (optionnel)"
    )

class CertificateRequest(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default='NomParDefaut')
    email = models.EmailField()
    certificate_type = models.CharField(max_length=100)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Pending")  # ex: Pending, Approved, Rejected

    def __str__(self):
        return f"Request for {self.name} - {self.certificate_type}"
    


class CertificatMedical(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)  # Lier le certificat au patient
    date = models.DateField()
    justification_medecin = models.TextField()

    def get_medecin(self):
        # Récupérer le premier médecin associé au patient (ajuste si nécessaire pour gérer plusieurs médecins)
        return self.patient.medecins.first()  # Si tu veux récupérer le premier médecin

    def __str__(self):
        return f"Certificat médical pour {self.patient.nom} {self.patient.prenom}"
